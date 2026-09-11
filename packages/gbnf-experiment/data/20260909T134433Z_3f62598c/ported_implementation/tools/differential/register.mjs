import { register } from 'node:module';
import { pathToFileURL } from 'node:url';
import { dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

register('./loader.mjs', pathToFileURL(`${dirname(fileURLToPath(import.meta.url))}/`));
