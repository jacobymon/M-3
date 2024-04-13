module.exports = {
    jest: {
        configure: {
          moduleNameMapper: { '^axios$': 'axios/dist/node/axios.cjs' },
        },
      },
}
