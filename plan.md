# Project Plan: Carbon-Aware Delivery B2B SaaS Portal

## 1. Vision
Deliver a comprehensive "Sustainability-as-a-Service" platform for logistics businesses. Instead of raw API endpoints, we provide an interactive enterprise portal where fleet managers can upload order data, view real-time carbon-optimized routes, and download certified ESG impact reports.

## 2. Infrastructure Stack (Student/Free Tier)
- **SaaS Portal (Frontend):** Next.js/React hosted on **Vercel** (Free Tier).
- **Authentication & Database:** **Supabase** (Free Tier) for user sign-ups, fleet profiles, and historical data storage.
- **Optimization Engine (Backend):** FastAPI + RL + OSRM hosted on **DigitalOcean Droplet** ($200 Student Credit).
- **Reports/Storage:** Supabase Storage or Vercel Blob for PDF/CSV report generation.

## 3. Implementation Steps

### Phase 1: SaaS Portal & Auth (The "Face")
- [ ] Initialize a Next.js project for the B2B portal.
- [ ] Integrate Supabase Auth for Business User Login/Sign-up.
- [ ] Create a "Fleet Management" UI to allow users to define their vehicle mix (EVs vs. Petrol).

### Phase 2: Live Optimization Engine
- [ ] Implement a protected backend service on DigitalOcean.
- [ ] Create an "Upload Orders" feature (CSV/JSON) that triggers the RL optimization engine.
- [ ] Build a "Live Map" view in the portal using Mapbox or Leaflet to show optimized routes.

### Phase 3: ESG Reporting & Analytics
- [ ] Develop an automated report generator that summarizes CO2 savings per week/month.
- [ ] Create a "Company Scorecard" comparing the business's performance against industry baselines.
- [ ] Implement a "Download PDF Report" feature for stakeholder presentations.

### Phase 4: Deployment & Scaling
- [ ] Containerize the full stack using Docker.
- [ ] Deploy the Engine to DigitalOcean and the Portal to Vercel.
- [ ] Setup custom domain (if available) and SSL.

## 4. Monetization Model (B2B SaaS)
- **Pilot (Free):** Up to 10 deliveries per day for small local businesses.
- **Pro ($299/mo):** Full fleet optimization, live tracking, and monthly ESG reports.
- **Enterprise (Custom):** Multi-city support, custom API integration, and white-labeled dashboards.
