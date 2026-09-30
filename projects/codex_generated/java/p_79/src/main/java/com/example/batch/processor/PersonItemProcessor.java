package com.example.batch.processor;

import com.example.batch.model.Person;
import com.example.batch.model.PersonInput;
import org.springframework.batch.item.ItemProcessor;

public class PersonItemProcessor implements ItemProcessor<PersonInput, Person> {

    @Override
    public Person process(PersonInput item) throws Exception {
        if (item.getAge() < 0) {
            throw new IllegalStateException("Age cannot be negative for " + item.getEmail());
        }
        return new Person(
                capitalize(item.getFirstName()),
                capitalize(item.getLastName()),
                item.getEmail().toLowerCase(),
                item.getAge()
        );
    }

    private String capitalize(String value) {
        if (value == null || value.isBlank()) {
            return value;
        }
        return value.substring(0, 1).toUpperCase() + value.substring(1).toLowerCase();
    }
}
