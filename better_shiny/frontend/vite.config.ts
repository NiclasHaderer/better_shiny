import {resolve} from 'path';
import {defineConfig} from 'vite';
import dts from 'vite-plugin-dts';

// https://vitejs.dev/guide/build.html#library-mode
export default defineConfig({
    build: {
        outDir: "../static",
        lib: {
            entry: resolve(__dirname, 'src/index.ts'),
            name: 'better-shiny',
            fileName: 'better-shiny',
        },
        sourcemap: true,
        emptyOutDir: true,
    },
    plugins: [
        dts(),
    ],
});