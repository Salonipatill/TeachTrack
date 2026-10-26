// Regenerate the Python adapter contract with the official @vercel/blob SDK.
// npm.cmd install --prefix .pytest_cache/blob-contract --ignore-scripts --no-audit --no-fund @vercel/blob@2.8.2
// node tools/build_blob_signing_fixture.mjs .pytest_cache/blob-contract/node_modules/@vercel/blob
// Uses synthetic offline keys only; never connects to a Blob store.
import {readFile, mkdir, writeFile} from 'node:fs/promises';
import {resolve, join} from 'node:path';
import {pathToFileURL} from 'node:url';

const packagePath = resolve(process.argv[2]);
const packageInfo = JSON.parse(await readFile(join(packagePath, 'package.json'), 'utf8'));
if (packageInfo.name !== '@vercel/blob') throw new Error('Expected the official @vercel/blob package.');
const {presignUrl} = await import(pathToFileURL(join(packagePath, 'dist/index.js')));
const now = 1700000000000;
Date.now = () => now;
const pathname = 'blob/123/' + 'a'.repeat(32) + '/AI notes.png';
const payload = {storeId: 'store_teststore', ownerId: 'fixture-owner', pathname,
  operations: ['put', 'get', 'head'], validUntil: now + 15 * 60 * 1000,
  iat: now, maximumSizeInBytes: 30 * 1024 * 1024, allowedContentTypes: ['image/png']};
const material = {delegationToken: Buffer.from(JSON.stringify(payload)).toString('base64url') + '.fixture-hmac',
  clientSigningToken: 'offline-fixture-signing-key-only', validUntil: payload.validUntil};
const cases = [];
for (const operation of ['put', 'get', 'head']) {
  const options = {operation, pathname, access: 'private'};
  if (operation === 'put') Object.assign(options, {allowedContentTypes: ['image/png'],
    maximumSizeInBytes: 30 * 1024 * 1024, addRandomSuffix: false, allowOverwrite: false});
  cases.push({operation, url: (await presignUrl(material, options)).presignedUrl});
}
const output = resolve('ClassApp/fixtures/blob_signing_contract.json');
await mkdir(resolve('ClassApp/fixtures'), {recursive: true});
await writeFile(output, JSON.stringify({sdk: '@vercel/blob@' + packageInfo.version, now, material, cases}, null, 2) + '\n');
console.log('Generated 3 offline signing fixtures with ' + packageInfo.name + '@' + packageInfo.version);
