import chokidar from 'chokidar';
import { hideBin } from 'yargs/helpers';
import yargs from 'yargs/yargs';

const argv = yargs(hideBin(process.argv))
  .option('paths', {
    alias: 'p',
    type: 'array',
    demandOption: true,
    describe: 'Files or directories to watch'
  })
  .option('debounce', {
    alias: 'd',
    type: 'number',
    default: 300,
    describe: 'Debounce delay in milliseconds'
  })
  .option('ignore', {
    alias: 'i',
    type: 'array',
    default: ['**/node_modules/**', '**/.git/**'],
    describe: 'Glob patterns to ignore'
  })
  .help()
  .argv;

const pendingEvents = new Map();

function scheduleEvent(key, callback, delay) {
  if (pendingEvents.has(key)) {
    clearTimeout(pendingEvents.get(key));
  }
  const timeout = setTimeout(() => {
    pendingEvents.delete(key);
    callback();
  }, delay);
  pendingEvents.set(key, timeout);
}

const watcher = chokidar.watch(argv.paths, {
  ignored: argv.ignore,
  ignoreInitial: false,
  persistent: true,
  depth: Infinity
});

watcher
  .on('add', (path) => {
    scheduleEvent(`add:${path}`, () => {
      console.log(`[ADD]    ${path}`);
    }, argv.debounce);
  })
  .on('change', (path) => {
    scheduleEvent(`change:${path}`, () => {
      console.log(`[CHANGE] ${path}`);
    }, argv.debounce);
  })
  .on('unlink', (path) => {
    scheduleEvent(`unlink:${path}`, () => {
      console.log(`[DELETE] ${path}`);
    }, argv.debounce);
  })
  .on('addDir', (path) => console.log(`[DIR+ ]  ${path}`))
  .on('unlinkDir', (path) => console.log(`[DIR- ]  ${path}`))
  .on('error', (error) => console.error('Watcher error:', error));

console.log('Watching paths:', argv.paths.join(', '));
