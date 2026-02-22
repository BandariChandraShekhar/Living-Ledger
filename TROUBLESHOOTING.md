# 🔧 Troubleshooting Guide

## ❌ Problem: Search Returns No Results

### Symptom
- You open http://localhost:8000
- You type a search query like "email" or "customer email"
- Click Search
- Nothing happens or you see "No Results Found"

### Root Cause
**The database hasn't been processed yet!** The API server starts empty - you need to process the database first to populate the metadata.

### ✅ Solution (3 Steps)

#### Step 1: Make Sure Server is Running
Check your terminal - you should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

If not, start it:
```bash
cd living_ledger
python api.py
```

#### Step 2: Process the Database

**Option A: Use the Demo Script (Recommended)**
```bash
# Open a NEW terminal window (keep the server running)
cd living_ledger
python demo.py
```

This will:
- Process the sample database
- Create 21 metadata entities
- Show you the results
- Populate the system with searchable data

**Option B: Use the API Endpoint**

Open your browser and go to:
```
http://localhost:8000/docs
```

1. Find `POST /api/v1/process`
2. Click "Try it out"
3. You'll see this JSON:
```json
{
  "connection_string": "sample_data.db",
  "source_type": "sqlite",
  "sampling_rate": 0.1,
  "max_sample_size": 10000
}
```
4. Click "Execute"
5. Wait 10-20 seconds
6. You'll see:
```json
{
  "entities_created": 21,
  "entities_updated": 0,
  "drift_alerts": [],
  "errors": []
}
```

**Option C: Use cURL**
```bash
curl -X POST http://localhost:8000/api/v1/process \
  -H "Content-Type: application/json" \
  -d '{
    "connection_string": "sample_data.db",
    "source_type": "sqlite",
    "sampling_rate": 0.1,
    "max_sample_size": 10000
  }'
```

#### Step 3: Verify Data is Loaded

Go to http://localhost:8000/docs and try:
```
GET /api/v1/stats
```

You should see:
```json
{
  "total_entities": 21,
  "certified": 0,
  "uncertified": 21,
  ...
}
```

If `total_entities` is 21, you're good! ✅

#### Step 4: Try Searching Again

Now go back to http://localhost:8000 and search for:
- `email`
- `customer email`
- `order amount`
- `product price`

You should see results! 🎉

---

## 🎯 Quick Fix Command

If you just want to get it working fast:

```bash
# Terminal 1: Start server
cd living_ledger
python api.py

# Terminal 2: Process database
cd living_ledger
python demo.py
```

Then refresh http://localhost:8000 and search!

---

## 🔍 Other Common Issues

### Issue: "Connection refused" or "Can't reach localhost:8000"

**Solution:**
1. Make sure the server is running (check terminal)
2. Try http://127.0.0.1:8000 instead
3. Check if port 8000 is blocked by firewall

### Issue: "Module not found" errors

**Solution:**
```bash
cd living_ledger
pip install -r requirements.txt
```

### Issue: "sample_data.db not found"

**Solution:**
```bash
cd living_ledger
python create_sample_db.py
```

### Issue: Search is slow

**Solution:**
- This is normal for first search (building indexes)
- Subsequent searches will be faster
- The demo database is small, so it should be quick

### Issue: Statistics show 0 entities

**Solution:**
You haven't processed the database yet. See "Solution" above.

---

## 📊 Expected Behavior

### After Processing Database:
- **Total Entities**: 21
- **Tables**: customers, orders, products
- **Searchable columns**: email, phone, name, amount, price, status, etc.

### Search Examples That Should Work:
```
email          → customers.email
customer       → customers.* columns
order          → orders.* columns
amount         → orders.total_amount
price          → products.price
status         → customers.status, orders.status
phone          → customers.phone
name           → customers.first_name, customers.last_name, products.product_name
```

---

## 🎓 Understanding the System

### Why Do I Need to Process First?

The Living Ledger doesn't automatically scan your database on startup. This is by design:

1. **Performance**: Processing can take time for large databases
2. **Control**: You decide when to scan
3. **Privacy**: You control what gets analyzed

### What Happens During Processing?

1. Connects to database
2. Extracts table schemas (DDL)
3. Samples 10% of data (configurable)
4. Calculates statistics (entropy, distribution, etc.)
5. Generates AI descriptions
6. Stores in Semantic Shadow Layer
7. Makes data searchable

### How Often Should I Process?

- **First time**: Always process to populate data
- **After schema changes**: Process again to update
- **Periodic**: Process weekly/monthly to detect drift
- **On-demand**: Process when you add new tables

---

## 🔄 Complete Reset (If Nothing Works)

If you're having persistent issues:

```bash
# Stop the server (Ctrl+C)

# Navigate to project
cd living_ledger

# Recreate database
python create_sample_db.py

# Process it
python demo.py

# Start server
python api.py

# Open browser
# http://localhost:8000
```

---

## ✅ Verification Checklist

Before searching, verify:

- [ ] Server is running (terminal shows "Uvicorn running...")
- [ ] Database exists (sample_data.db file in living_ledger folder)
- [ ] Database has been processed (run demo.py or use /api/v1/process)
- [ ] Statistics show 21 entities (check /api/v1/stats)
- [ ] Browser can access http://localhost:8000

If all checked, search should work! ✅

---

## 🆘 Still Not Working?

### Check Server Logs

Look at the terminal where the server is running. You should see:
```
INFO:     127.0.0.1:xxxxx - "POST /api/v1/search HTTP/1.1" 200 OK
```

If you see errors, that's the clue!

### Check Browser Console

1. Open browser developer tools (F12)
2. Go to Console tab
3. Try searching
4. Look for error messages

Common errors:
- `Failed to fetch` → Server not running
- `404 Not Found` → Wrong URL
- `CORS error` → Browser security issue (shouldn't happen with our setup)

### Test API Directly

```bash
# Test if server is responding
curl http://localhost:8000/api/v1/stats

# Test search
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "email", "limit": 10}'
```

If cURL works but browser doesn't, it's a browser issue.

---

## 💡 Pro Tips

1. **Always process first**: Run `python demo.py` before using the web interface
2. **Keep server running**: Don't close the terminal with the server
3. **Use two terminals**: One for server, one for commands
4. **Check stats first**: Visit /api/v1/stats to verify data is loaded
5. **Try simple searches**: Start with "email" or "status" before complex queries

---

## 📞 Quick Reference

### To Fix "No Search Results":
```bash
# Terminal 1
cd living_ledger
python api.py

# Terminal 2
cd living_ledger
python demo.py

# Browser
http://localhost:8000
```

### To Verify System is Working:
```bash
# Check stats
curl http://localhost:8000/api/v1/stats

# Should return:
# {"total_entities": 21, ...}
```

### To Reset Everything:
```bash
cd living_ledger
python create_sample_db.py
python demo.py
python api.py
```

---

**The most common issue is forgetting to process the database first!**

**Solution: Run `python demo.py` before searching.** 🚀

---

## 🎬 Correct Startup Sequence

```
1. cd living_ledger
2. python create_sample_db.py  (if database doesn't exist)
3. python demo.py              (process the database)
4. python api.py               (start the server)
5. Open http://localhost:8000  (use the web interface)
6. Search!                     (now it works!)
```

**Or use the automated script:**
```bash
cd living_ledger
python setup_and_run.py
# Answer 'y' to both prompts
```

This does everything automatically! ✅
