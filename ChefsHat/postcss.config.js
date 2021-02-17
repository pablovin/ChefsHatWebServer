module.exports = (env, args) => ({
  sourceMap: true,
  plugins: {
    'cssnano': {
      preset: 'default',
      discardComments: {
        removeAll: true,
      },
    },
  }
});