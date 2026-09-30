#!/usr/bin/env node

import { Command } from 'commander';
import ora from 'ora';
import cliProgress from 'cli-progress';
import chalk from 'chalk';
import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Error handler utility
class TaskError extends Error {
  constructor(message, code = 'TASK_ERROR') {
    super(message);
    this.name = 'TaskError';
    this.code = code;
  }
}

// Simulated task utilities
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// Task: Build command
async function buildTask(options) {
  const spinner = ora('Starting build process...').start();

  try {
    // Validate options
    if (!['development', 'production'].includes(options.env)) {
      throw new TaskError(
        `Invalid environment: ${options.env}. Must be 'development' or 'production'`,
        'INVALID_ENV'
      );
    }

    spinner.text = 'Cleaning build directory...';
    await sleep(1000);

    spinner.text = `Building for ${options.env} environment...`;
    await sleep(1500);

    spinner.text = 'Optimizing assets...';
    await sleep(1200);

    spinner.text = 'Generating output files...';
    await sleep(800);

    spinner.succeed(chalk.green(`Build completed successfully for ${options.env}!`));

    console.log(chalk.gray('\nBuild summary:'));
    console.log(chalk.cyan('  Environment:'), options.env);
    console.log(chalk.cyan('  Output:'), './dist');
    console.log(chalk.cyan('  Time:'), '4.5s');

  } catch (error) {
    spinner.fail(chalk.red('Build failed!'));
    throw error;
  }
}

// Task: Deploy command
async function deployTask(options) {
  const spinner = ora('Preparing deployment...').start();

  try {
    if (!options.target) {
      throw new TaskError('Deployment target is required', 'MISSING_TARGET');
    }

    spinner.text = `Connecting to ${options.target}...`;
    await sleep(1000);

    spinner.text = 'Uploading files...';
    await sleep(2000);

    spinner.text = 'Running health checks...';
    await sleep(1500);

    spinner.succeed(chalk.green(`Deployed successfully to ${options.target}!`));

  } catch (error) {
    spinner.fail(chalk.red('Deployment failed!'));
    throw error;
  }
}

// Task: Test command with progress bar
async function testTask(options) {
  console.log(chalk.blue.bold('\n Running test suite...\n'));

  try {
    const tests = [
      'Unit tests',
      'Integration tests',
      'E2E tests',
      'Performance tests',
      'Security tests'
    ];

    const progressBar = new cliProgress.SingleBar({
      format: chalk.cyan('{bar}') + ' | {percentage}% | {value}/{total} | {test}',
      barCompleteChar: '\u2588',
      barIncompleteChar: '\u2591',
      hideCursor: true
    });

    progressBar.start(tests.length, 0, { test: 'Starting...' });

    for (let i = 0; i < tests.length; i++) {
      progressBar.update(i, { test: tests[i] });
      await sleep(800);

      // Simulate random test failure if verbose mode
      if (options.verbose && i === 2 && Math.random() > 0.7) {
        progressBar.stop();
        throw new TaskError(
          `${tests[i]} failed: Assertion error in test_auth.js:42`,
          'TEST_FAILURE'
        );
      }

      progressBar.update(i + 1, { test: tests[i] });
    }

    progressBar.stop();

    console.log(chalk.green('\n✓ All tests passed!\n'));
    console.log(chalk.gray('Test summary:'));
    console.log(chalk.cyan('  Total:'), tests.length);
    console.log(chalk.cyan('  Passed:'), tests.length);
    console.log(chalk.cyan('  Failed:'), 0);
    console.log(chalk.cyan('  Duration:'), '4.0s');

  } catch (error) {
    throw error;
  }
}

// Task: Install dependencies with progress
async function installTask(options) {
  console.log(chalk.blue.bold('\n Installing dependencies...\n'));

  try {
    const packages = [
      'express@4.18.2',
      'lodash@4.17.21',
      'axios@1.6.0',
      'dotenv@16.3.1',
      'mongoose@8.0.0',
      'jest@29.7.0',
      'eslint@8.50.0',
      'typescript@5.2.2'
    ];

    const progressBar = new cliProgress.SingleBar({
      format: 'Installing |' + chalk.green('{bar}') + '| {percentage}% | {pkg}',
      barCompleteChar: '█',
      barIncompleteChar: '░',
      hideCursor: true
    });

    progressBar.start(packages.length, 0, { pkg: '' });

    for (let i = 0; i < packages.length; i++) {
      progressBar.update(i, { pkg: packages[i] });
      await sleep(options.fast ? 200 : 600);
      progressBar.update(i + 1, { pkg: packages[i] });
    }

    progressBar.stop();

    console.log(chalk.green('\n✓ All dependencies installed successfully!\n'));
    console.log(chalk.gray(`Installed ${packages.length} packages`));

  } catch (error) {
    throw new TaskError('Failed to install dependencies', 'INSTALL_ERROR');
  }
}

// Task: Database migration
async function migrateTask(options) {
  const spinner = ora('Preparing database migration...').start();

  try {
    spinner.text = 'Connecting to database...';
    await sleep(800);

    spinner.text = 'Reading migration files...';
    await sleep(600);

    const migrations = ['001_create_users', '002_add_indexes', '003_add_roles'];
    spinner.stop();

    console.log(chalk.blue('\nRunning migrations:\n'));

    for (const migration of migrations) {
      const migrationSpinner = ora(migration).start();
      await sleep(700);

      if (options.dryRun) {
        migrationSpinner.info(chalk.yellow(`${migration} (dry run)`));
      } else {
        migrationSpinner.succeed(chalk.green(migration));
      }
    }

    console.log(chalk.green('\n✓ Migration completed!\n'));

    if (options.dryRun) {
      console.log(chalk.yellow('Note: This was a dry run. No changes were made.'));
    }

  } catch (error) {
    spinner.fail(chalk.red('Migration failed!'));
    throw error;
  }
}

// Global error handler
function handleError(error) {
  console.error('\n' + chalk.red.bold('Error: ') + chalk.red(error.message));

  if (error.code) {
    console.error(chalk.gray('Error code:'), chalk.yellow(error.code));
  }

  if (error.stack && process.env.DEBUG) {
    console.error(chalk.gray('\nStack trace:'));
    console.error(chalk.gray(error.stack));
  } else {
    console.error(chalk.gray('\nRun with DEBUG=1 for full stack trace'));
  }

  process.exit(1);
}

// Main CLI setup
const program = new Command();

program
  .name('taskrun')
  .description('A powerful CLI task runner with progress indicators')
  .version('1.0.0')
  .option('-d, --debug', 'Enable debug mode');

// Build command
program
  .command('build')
  .description('Build the project')
  .option('-e, --env <environment>', 'Build environment', 'development')
  .action(async (options) => {
    try {
      await buildTask(options);
    } catch (error) {
      handleError(error);
    }
  });

// Deploy command
program
  .command('deploy')
  .description('Deploy the application')
  .option('-t, --target <target>', 'Deployment target (staging/production)')
  .action(async (options) => {
    try {
      await deployTask(options);
    } catch (error) {
      handleError(error);
    }
  });

// Test command
program
  .command('test')
  .description('Run test suite')
  .option('-v, --verbose', 'Verbose output')
  .option('-c, --coverage', 'Generate coverage report')
  .action(async (options) => {
    try {
      await testTask(options);
    } catch (error) {
      handleError(error);
    }
  });

// Install command
program
  .command('install')
  .description('Install dependencies')
  .option('-f, --fast', 'Fast installation mode')
  .action(async (options) => {
    try {
      await installTask(options);
    } catch (error) {
      handleError(error);
    }
  });

// Migrate command
program
  .command('migrate')
  .description('Run database migrations')
  .option('--dry-run', 'Simulate migration without applying changes')
  .action(async (options) => {
    try {
      await migrateTask(options);
    } catch (error) {
      handleError(error);
    }
  });

// Parse arguments
program.parse(process.argv);

// Show help if no command provided
if (!process.argv.slice(2).length) {
  program.outputHelp();
}
