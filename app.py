import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'TechifyBots'

if __name__ == "__main__":
    # Render থেকে প্রাপ্ত পোর্ট ব্যবহার করুন, যদি না থাকে তাহলে 5000 পোর্টে রান করবে
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)  # host="0.0.0.0" দিয়ে সকল অ্যাড্রেস থেকে অ্যাক্সেসযোগ্য করা হবে