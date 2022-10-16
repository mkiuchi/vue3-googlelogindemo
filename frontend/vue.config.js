const { defineConfig } = require('@vue/cli-service')
// const { ProvidePlugin } = require('webpack')
module.exports = defineConfig({
  transpileDependencies: true,

  pluginOptions: {
    vuetify: {
			// https://github.com/vuetifyjs/vuetify-loader/tree/next/packages/vuetify-loader
		}
  },

  configureWebpack: {
    /* plugins: [
      new ProvidePlugin({
        process: 'process/browser'
      })
    ], */
    resolve: {
      fallback: {
        "https": false,
        "crypto": false,
        "child_process": false,
        "fs": false,
      }
    }
  }
})
