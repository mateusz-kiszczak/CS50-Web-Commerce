module.exports = { 
    proxy: "127.0.0.1:8000", 
    files: [ 
        './auctions/templates/auctions/*.html', 
        './auctions/static/auctions/*.css', ], 
    watchOptions: { 
        ignored: 'node_modules/**',
    },
};