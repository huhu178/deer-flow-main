module.exports = {
  root: true,
  extends: ['next/core-web-vitals', 'plugin:@typescript-eslint/recommended'],
  rules: {
    // Disable import ordering and unused vars complaints for app/*
    'import/order': 'off',
    '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
    '@typescript-eslint/prefer-nullish-coalescing': 'off',
  },
  overrides: [
    {
      // Specifically turn off import/order in the app directory
      files: ['src/app/**/*.{ts,tsx}'],
      rules: {
        'import/order': 'off',
      },
    },
  ],
}; 