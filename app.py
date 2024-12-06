from flask import Flask, request, render_template, send_file
import yfinance as yf
import io
import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend for matplotlib
import matplotlib.pyplot as plt

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    ticker = None
    sector = None
    market_cap = None
    summary = None

    if request.method == "POST":
        ticker = request.form.get("ticker")
        if ticker:
            try:
                start_date = "2023-01-03"
                end_date = "2023-12-29"
                df = yf.download(ticker, start=start_date, end=end_date)
                if df.empty:
                    result = "No data found for this ticker."
                else:
                    result = df.to_html(classes="table table-striped")

                    # Attempt to fetch additional company info
                    ticker_obj = yf.Ticker(ticker)
                    company_info = {}
                    try:
                        company_info = ticker_obj.info  # May not work on newer yfinance versions
                    except:
                        pass

                    sector = company_info.get("sector", "N/A")
                    market_cap = company_info.get("marketCap", "N/A")
                    summary = company_info.get("longBusinessSummary", "No summary available.")
            except Exception as e:
                result = f"An error occurred: {e}"
        else:
            result = "Please enter a ticker."

    return render_template("index.html",
                           result=result,
                           ticker=ticker,
                           sector=sector,
                           market_cap=market_cap,
                           summary=summary)


@app.route("/plot/<ticker>")
def plot(ticker):
    try:
        start_date = "2023-01-03"
        end_date = "2023-12-29"
        df = yf.download(ticker, start=start_date, end=end_date)
        if df.empty:
            return "No data to plot."

        plt.figure(figsize=(10, 5))
        plt.plot(df.index, df["Close"], label=f"{ticker.upper()} Close")
        plt.title(f"{ticker.upper()} Stock Prices")
        plt.xlabel("Date")
        plt.ylabel("Price (USD)")
        plt.grid(True)
        plt.legend()

        img = io.BytesIO()
        plt.savefig(img, format="png")
        img.seek(0)
        plt.close()

        return send_file(img, mimetype="image/png")
    except Exception as e:
        return f"An error occurred while generating the plot: {e}"


@app.route("/plot_comparison/<ticker>")
def plot_comparison(ticker):
    try:
        start_date = "2023-01-03"
        end_date = "2023-12-29"
        # Download both the company's data and SPY for the same time period
        df_company = yf.download(ticker, start=start_date, end=end_date)
        df_spy = yf.download("SPY", start=start_date, end=end_date)

        if df_company.empty or df_spy.empty:
            return "Not enough data to compare."

        # Normalize both time series to start at 1 for easy comparison
        df_company_norm = df_company["Close"] / df_company["Close"].iloc[0]
        df_spy_norm = df_spy["Close"] / df_spy["Close"].iloc[0]

        plt.figure(figsize=(10, 5))
        plt.plot(df_company_norm.index, df_company_norm, label=ticker.upper())
        plt.plot(df_spy_norm.index, df_spy_norm, label="SPY (S&P 500)", color='orange')
        plt.title(f"Performance Comparison: {ticker.upper()} vs. S&P 500")
        plt.xlabel("Date")
        plt.ylabel("Normalized Price (Start=1)")
        plt.grid(True)
        plt.legend()

        img = io.BytesIO()
        plt.savefig(img, format="png")
        img.seek(0)
        plt.close()

        return send_file(img, mimetype="image/png")
    except Exception as e:
        return f"An error occurred while generating the comparison plot: {e}"


if __name__ == "__main__":
    app.run(debug=True)
