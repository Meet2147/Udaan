import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}', './lib/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: '#0e7490',
        ink: '#0f172a',
        sand: '#f8fafc',
      },
    },
  },
  plugins: [],
};

export default config;
