module.exports = {
    apps : [{
      name: "AceTaffy-Weibo",
      script: "./app.py",
      interpreter: "python",
      args: '0',
      autorestart: true,
      watch: false,
      pid_file: './weibo.pid',
    }]
  }
  