const path = require('path');
const srcPath = './static/src/';
const devMode = process.env.NODE_ENV !== 'production'

module.exports = {
    // Default mode for Webpack is production.
    mode: devMode ? 'development' : 'production',

    // Path to your entry point. From this file Webpack will begin his work
    entry: [
         // TypeScript
         `${srcPath}ts/game.ts`,
          `${srcPath}ts/startNewGame.ts`,
         // SCSS
         `${srcPath}scss/base.scss`,
         `${srcPath}scss/game.scss`,
         `${srcPath}scss/rules.scss`,
         `${srcPath}scss/gameFinished.scss`,
         `${srcPath}scss/index.scss`,
         `${srcPath}scss/selectAdversaries.scss`,
         `${srcPath}scss/disclaimer.scss`,
         `${srcPath}scss/startNewGame.scss`,
         `${srcPath}scss/ranking.scss`,
         `${srcPath}scss/ruleBook.scss`,

    ],

    // Path and filename of your result bundle.
    output: {
        path: path.resolve(__dirname, 'static'),
    },
    module: {
        rules: [
            {
                test: /\.tsx?$/i,
                exclude: /node_modules/,
                use: [
                    {
                        loader: 'file-loader',
                        options: { 
                            name: './js/[name].js'
                        }
                    },
                    'ts-loader'
                ],
            },
            {
                test: /\.scss$/i,
                exclude: /node_modules/,
                use: [
                    {
                        loader: 'file-loader',
                        options: { 
                            name: './css/[name].css'
                        }
                    },
                    'extract-loader',
                    {
                        loader: 'css-loader?-url',
                        options: {
                            sourceMap: true,
                            importLoaders: 2
                        }
                    },
                    'postcss-loader',
                    {
                        loader: 'sass-loader',
                        options: {
                            sourceMap: true,
                            implementation: require('sass')
                        }
                    }
                ]
            },
            {
                test: /\.(png|jpe?g|gif|svg)$/i,
                exclude: /node_modules/,
                use: [
                    {
                        loader: 'file-loader',
                        options: { 
                            outputPath: './static/images'
                        }
                    }
                ]
            }
        ]
    },
};