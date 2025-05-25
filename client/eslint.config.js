import stylistic from '@stylistic/eslint-plugin';
import reactPlugin from 'eslint-plugin-react';

export default [
  // Define which files to include/exclude
  {
    ignores: ['dist', 'node_modules'],
  },

  // Apply to all JS/JSX files
  {
    files: ['**/*.{js,jsx}'],
    plugins: {
      react: reactPlugin,
    },
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'module',
      parserOptions: {
        ecmaFeatures: {
          jsx: true,
        },
      },
    },
    // React specific settings
    settings: {
      react: {
        version: 'detect',
      },
    },
    rules: {
      // React rules
      'react/jsx-uses-react': 'error',
      'react/jsx-uses-vars': 'error',
      'react/react-in-jsx-scope': 'off', // For React 17+ (not needed)
    },
  },

  // Apply recommended stylistic rules
  stylistic.configs.recommended,

  // Customize stylistic rules
  stylistic.configs.customize({
    semi: true, // Semicolons are required
  }),
];
