#!/usr/bin/env node

import { Command } from 'commander';

const program = new Command();

program
    .version('1.0.0')
    .description('A command-line task runner');

program
    .command('task1')
    .description('Run the first task')
    .action(async () => {
        const ora = (await import('ora')).default;
        const spinner = ora('Running task 1...').start();
        try {
            // Simulate a long-running task
            await new Promise(resolve => setTimeout(resolve, 2000));
            spinner.succeed('Task 1 completed successfully');
        } catch (error) {
            spinner.fail('Task 1 failed');
            console.error(error.message);
        }
    });

program
    .command('task2')
    .description('Run the second task')
    .action(async () => {
        const ora = (await import('ora')).default;
        const spinner = ora('Running task 2...').start();
        try {
            // Simulate a long-running task that fails
            await new Promise((resolve, reject) => setTimeout(() => reject(new Error('Something went wrong in task 2')), 2000));
            spinner.succeed('Task 2 completed successfully');
        } catch (error) {
            spinner.fail('Task 2 failed');
            console.error(error.message);
        }
    });

program.parse(process.argv);
