package com.example.batch.config;

import com.example.batch.model.Person;
import com.example.batch.model.PersonInput;
import com.example.batch.processor.PersonItemProcessor;
import jakarta.persistence.EntityManagerFactory;
import org.springframework.batch.core.Job;
import org.springframework.batch.core.Step;
import org.springframework.batch.core.configuration.annotation.EnableBatchProcessing;
import org.springframework.batch.core.job.builder.JobBuilder;
import org.springframework.batch.core.launch.support.RunIdIncrementer;
import org.springframework.batch.core.repository.JobRepository;
import org.springframework.batch.core.step.builder.StepBuilder;
import org.springframework.batch.item.ItemProcessor;
import org.springframework.batch.item.database.JpaItemWriter;
import org.springframework.batch.item.file.FlatFileItemReader;
import org.springframework.batch.item.file.builder.FlatFileItemReaderBuilder;
import org.springframework.batch.item.file.mapping.BeanWrapperFieldSetMapper;
import org.springframework.batch.item.file.transform.DelimitedLineTokenizer;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.io.ClassPathResource;
import org.springframework.orm.jpa.JpaTransactionManager;

@Configuration
@EnableBatchProcessing
public class BatchConfig {

    private final EntityManagerFactory entityManagerFactory;

    public BatchConfig(EntityManagerFactory entityManagerFactory) {
        this.entityManagerFactory = entityManagerFactory;
    }

    @Bean
    public FlatFileItemReader<PersonInput> reader() {
        return new FlatFileItemReaderBuilder<PersonInput>()
                .name("personItemReader")
                .resource(new ClassPathResource("input/persons.csv"))
                .linesToSkip(1)
                .delimited(DelimitedLineTokenizer.DELIMITER_COMMA)
                .names("firstName", "lastName", "email", "age")
                .fieldSetMapper(new BeanWrapperFieldSetMapper<>() {{
                    setTargetType(PersonInput.class);
                }})
                .build();
    }

    @Bean
    public ItemProcessor<PersonInput, Person> processor() {
        return new PersonItemProcessor();
    }

    @Bean
    public JpaItemWriter<Person> writer() {
        JpaItemWriter<Person> writer = new JpaItemWriter<>();
        writer.setEntityManagerFactory(entityManagerFactory);
        return writer;
    }

    @Bean
    public Step importStep(JobRepository jobRepository, JpaTransactionManager transactionManager) {
        return new StepBuilder("importStep", jobRepository)
                .<PersonInput, Person>chunk(5, transactionManager)
                .reader(reader())
                .processor(processor())
                .writer(writer())
                .faultTolerant()
                .retryLimit(3)
                .retry(IllegalStateException.class)
                .skipLimit(5)
                .skip(IllegalStateException.class)
                .build();
    }

    @Bean
    public Job importJob(JobRepository jobRepository, Step importStep) {
        return new JobBuilder("importJob", jobRepository)
                .incrementer(new RunIdIncrementer())
                .start(importStep)
                .build();
    }
}
