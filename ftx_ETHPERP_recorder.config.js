module.exports = {
    apps : [{
      name: "Recorder FTX ETH-PERP",
      script: "python3 -u orderbook_record_model.py FTX \"ETH-PERP\"",
      time: true,
      env: {
        NODE_ENV: "development",
      },
      env_production: {
        NODE_ENV: "production",
      }
    }]
  }