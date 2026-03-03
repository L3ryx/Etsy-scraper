FROM python:3.11-slim

WORKDIR /app

RUN mkdir -p .streamlit

COPY render_requirements.txt .
RUN pip install --no-cache-dir -r render_requirements.txt

COPY app.py .
COPY scraper.py .

RUN printf '[server]\nheadless = true\naddress = "0.0.0.0"\n' > .streamlit/config.toml

EXPOSE 10000

CMD streamlit run app.py --server.port=${PORT:-10000} --server.address=0.0.0.0 --server.headless=true --browser.gatherUsageStats=false
