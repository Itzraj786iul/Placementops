export default {
  "apps/web/**/*.{ts,tsx}": ["eslint --fix", "prettier --write"],
  "packages/**/*.{ts,tsx}": ["prettier --write"],
  "*.{json,md,css}": ["prettier --write"],
};
