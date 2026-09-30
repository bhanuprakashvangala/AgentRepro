#!/usr/bin/env node
import { Command } from 'commander';
import ora from 'ora';
import chalk from 'chalk';
import { SingleBar, Presets } from 'cli-progress';
import fs from 'fs/promises';
import path from 'path';
import { setTimeout as delay } from 'timers/promises';

const program = new Command();
program
  .name('tasker')
  .description('CLI task runner with progress feedback and error reporting')
  .version('1.0.0');

program
  .command('build')
  .description('Simulate project build process')
  .option('-s, --steps <number>', 'Number of build steps', '5')
  .action(async (options) => {
    const steps = Number(options.steps);
    if (Number.isNaN(steps) || steps <= 0) {
      console.error(chalk.red('steps must be a positive number'));
      process.exit(1);
    }

    const bar = new SingleBar({
      format: 'Build Progress |' + chalk.cyan('{bar}') + '| {percentage}% || {value}/{total} steps',
      hideCursor: true
    }, Presets.shades_classic);

    try {
      bar.start(steps, 0);
      for (let i = 1; i <= steps; i += 1) {
        await delay(300);
        bar.update(i);
      }
      bar.stop();
      console.log(chalk.green('Build completed successfully.'));
    } catch (error) {
      bar.stop();
      console.error(chalk.red('Build failed:'), error.message);
      process.exit(1);
    }
  });

program
  .command('deploy')
  .description('Simulate deployment with spinner feedback')
  .option('-t, --target <env>', 'Deployment target', 'staging')
  .action(async ({ target }) => {
    const spinner = ora(`Deploying to ${target}...`).start();
    try {
      await delay(2000);
      if (target === 'production') {
        spinner.succeed('Deployment to production successful.');
      } else {
        spinner.succeed(`Deployment to ${target} successful.`);
      }
    } catch (error) {
      spinner.fail('Deployment failed.');
      console.error(chalk.red(error.message));
      process.exit(1);
    }
  });

program
  .command('backup <directory>')
  .description('Create compressed archive of a directory (simulated)')
  .action(async (directory) => {
    const spinner = ora(`Scanning directory ${directory}`).start();
    try {
      const stats = await fs.stat(directory);
      if (!stats.isDirectory()) {
        throw new Error('Path is not a directory');
      }
      const files = await fs.readdir(directory);
      spinner.text = `Processing ${files.length} files...`;
      await delay(1500);
      const archivePath = path.resolve(`${directory.replace(/[\W]+/g, '_')}.zip`);
      spinner.succeed(`Backup archive created at ${archivePath}`);
    } catch (error) {
      spinner.fail('Backup failed.');
      console.error(chalk.red(error.message));
      process.exit(1);
    }
  });

program
  .command('clean')
  .description('Clean build artifacts (example command)')
  .action(async () => {
    const spinner = ora('Cleaning artifacts...').start();
    try {
      await delay(1000);
      spinner.succeed('Clean complete.');
    } catch (error) {
      spinner.fail('Clean failed.');
      console.error(chalk.red(error.message));
      process.exit(1);
    }
  });

program.parseAsync(process.argv).catch((error) => {
  console.error(chalk.red('Unexpected error:'), error.message);
  process.exit(1);
});
