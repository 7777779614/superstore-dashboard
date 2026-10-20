# Global Superstore — Profit & Discount Dashboard

**Team:** &lt;填你的组号/名字&gt;
**App URL:** &lt;部署后填&gt;
**Dataset:** [Global Superstore (Kaggle)](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final)

---

## Step 1 · Dataset and Decision-Maker

### Dataset
We use the **Global Superstore** dataset from Kaggle: 51,290 rows, covering orders from **Jan 2011 to Dec 2014** across 147 countries. Each row is one order line (one product in one order). Columns include Sales, Profit, Discount, Quantity, Category, Sub-Category, Segment, Region, Customer, Order.Date, etc. No missing values. The dataset is synthetic retail data modeled on a real multinational office/technology/furniture retailer.

We picked it because the business question is concrete: **which product lines sell well but lose money, and which discounts are destroying margin?** That question is answered by the columns the dataset already contains.

### Decision-Maker
**One person:** the **Regional Sales Manager** for a major region (e.g. North America / APAC).
- Responsible for P&L of their region.
- Signs off on discount levels and promo plans by product category.
- Does not care about customer-level churn or supply chain — that's someone else's job.

A dashboard built for "everyone" ends up useful to no one, so we designed every element around this single role.

---

## Step 2 · Justify the Dashboard

**Q1. Who looks at it, and how often?**
The Regional Sales Manager opens it **every Monday morning** before the weekly pricing meeting, and ad-hoc whenever a big promo is being proposed.

**Q2. What decision does it support?**
> *If the Regional Sales Manager sees a Sub-Category with high Sales but negative or near-zero Profit (e.g. Tables at –8.5% margin), or a discount band whose Profit is negative (>30% discount band lost $793K in this dataset), they will freeze new discounts on that line and re-price before the next promo cycle.*

**Q3. What do they do today without it?**
They pull a raw CSV from the warehouse system, pivot it in Excel, and wait for an analyst. That cycle takes 2–3 days, and in the meantime loss-making discounts keep running. Estimated cost: every week of delay is another ~$15K–$30K of negative-margin sales shipped.

**Q4. Why a dashboard instead of a weekly email / report / alert?**
The same questions recur every week (which lines are bleeding? which regions? which discount level?), but the answer changes as new orders land. A static report can't be sliced by Region × Category × Year on the fly; an email would bury the number; an alert only fires after a threshold is already breached. The dashboard lets the manager drill from "is anything wrong" → "which line" → "which orders" in one page.

---

## Step 3 · What We Show (and What We Cut)

### What's on the page (top to bottom)

| Position | Element | Why it's there |
|---|---|---|
| Top | 4 headline metrics: **Total Sales, Total Profit, Profit Margin, Loss-making orders** | Answers "is anything wrong right now?" in 5 seconds. |
| Middle 1 | **Horizontal bar: Profit by Sub-Category**, colored red→green | Directly surfaces the manager's key question: which product lines sell but lose money. Tables is the only negative bar — immediately visible. |
| Middle 2 | **Bar: Profit by Discount band** | Shows the empirical finding: >30% discount band lost $793K overall. Tells the manager *where* to cut discounts. |
| Sidebar filters | Year, Category, Region | Realistic slices this role actually uses. No 10 sliders. |
| Bottom (collapsed) | Last 200 underlying orders table | For when the manager wants to drill into a specific deal. Hidden by default so it doesn't crowd the page. |

### Two things we chose NOT to show, and why

1. **Map of countries / customer geography.** EDA showed sales are concentrated in a handful of markets and a choropleth would look pretty but would not change any pricing or discount decision — the manager already knows which regions matter. It would add visual noise without changing an action.
2. **Customer Segment breakdown (Consumer / Corporate / Home Office).** The numbers are broadly similar (~11–12% margin each). Segment mix does not explain *why* some lines lose money; discount and Sub-Category do. We'd rather show one strong chart than two weak ones.

### Things in the data that could mislead a viewer

- **"Sales" looks healthy on its own.** Tables sold $757K — a respectable number — but lost $64K. That is exactly why we lead with Profit and Margin, not Sales, and why the Sub-Category chart is sorted by Profit rather than Sales.
- **Discount=0% rows inflate the good margin.** 29,000 of 51,290 rows carry no discount and post 25%+ margin. The dashboard's discount-band chart makes this explicit instead of hiding it behind an average.
- **The data is frozen at Dec 2014.** We put a caption on the page: *"Data: Jan 2011 – Dec 2014, Kaggle snapshot. Production refresh: nightly."* so no reader mistakes it for live numbers.

### Page order rationale
People read top to bottom and many never scroll. So: headline numbers first (answer "is anything wrong"), then the two charts that explain *why*, then the optional detail table at the bottom.

---

## Step 4 · Refresh Frequency

1. **Data refresh cadence:** In production, sales data refreshes **nightly** from the point-of-sale / order system. Real-time would add cost without changing any decision — pricing decisions are made weekly, not by the second.
2. **Review cadence:** The manager reviews the dashboard **every Monday morning** before the weekly pricing meeting. (Same as refresh cadence — but they're different ideas: refresh = when new data lands; review = when a human opens the page.)
3. **One tracked metric & threshold:** We track **overall Profit Margin** (target ≥ 12%). If margin drops below **10% for two consecutive weeks**, that triggers a pricing review meeting — someone picks up the phone.
4. **Cost of stale data:** If the dashboard is a week out of date, loss-making promos that should have been killed keep running — roughly $15K–$30K of negative-margin sales per week, per region.

On the deployed app, the caption line reads:
> *Data: Jan 2011 – Dec 2014, Kaggle snapshot. In production: refresh nightly, reviewed every Monday.*

---

## How to run locally

```bash
uv init superstore-dashboard
cd superstore-dashboard
uv add streamlit pandas plotly
# put app.py and superstore.csv in this folder
streamlit run app.py
```

Then push to your own public GitHub repo and deploy on [Streamlit Community Cloud](https://share.streamlit.io/), set Python version to 3.14 under Advanced settings.
