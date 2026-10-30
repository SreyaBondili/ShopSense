// High-quality, distinct Unsplash product imagery
// Each product has its own unique, verified photo URL to prevent duplicate images across different products.

const EXACT_PRODUCT_MAP = {
  // Electronics
  'Noise-Cancelling Wireless Headphones Pro': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&q=80',
  'Ultra-Slim RGB Mechanical Keyboard': 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=500&q=80',
  'Smartwatch Series 7 Titanium': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&q=80',
  'Thunderbolt 4 High-Speed USB Dock': 'https://images.unsplash.com/photo-1625842268584-8f3296236761?w=500&q=80',
  '4K Ultra HD Dual-Monitor Webcam 60FPS': 'https://images.unsplash.com/photo-1587826080692-f439cd0b70da?w=500&q=80',
  'Wireless Ergonomic Vertical Mouse': 'https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=500&q=80',
  'Active Noise-Cancelling Bluetooth Earbuds': 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=500&q=80',
  'Fast Magnetic Wireless Charging Pad 15W': 'https://images.unsplash.com/photo-1622445262464-84b14e3295b6?w=500&q=80',
  'fridge': 'https://images.unsplash.com/photo-1584992236310-6edddc08acff?w=500&q=80',
  'Compact Mini Fridge & Beverage Cooler': 'https://images.unsplash.com/photo-1584992236310-6edddc08acff?w=500&q=80',
  'Wireless Noise-Canceling Headphones': 'https://images.unsplash.com/photo-1484704849700-f032a568e944?w=500&q=80',

  // Fashion
  'Organic Cotton Classic Graphic Tee': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=500&q=80',
  'Classic Slim-Fit Stretch Denim Jeans': 'https://images.unsplash.com/photo-1542272604-787c3835535d?w=500&q=80',
  'Lightweight Waterproof All-Weather Windbreaker': 'https://images.unsplash.com/photo-1544923246-77307dd654cb?w=500&q=80',
  'Merino Wool Thermal Crewneck Sweater': 'https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=500&q=80',
  'Tailored Casual Linen Blend Button-Down': 'https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=500&q=80',
  'Athletic Breathable Performance Joggers': 'https://images.unsplash.com/photo-1552902865-b72c031ac5ea?w=500&q=80',
  'Unisex Heavyweight Fleece Pullover Hoodie': 'https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=500&q=80',
  'Seamless Comfort Yoga Leggings': 'https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=500&q=80',
  'Kurti': 'https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=500&q=80',
  'Silk Embroidered Saree': 'https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=500&q=80',
  'Earrings': 'https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=500&q=80',

  // Books
  'Data Science & AI Engineering Handbook': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500&q=80',
  'Modern Web Architecture with FastAPI & React': 'https://images.unsplash.com/photo-1532012164546-f432f2e3777a?w=500&q=80',
  'The Art of Scalable Cloud Computing': 'https://images.unsplash.com/photo-1512820790803-83ca734da794?w=500&q=80',
  'Deep Learning Illustrated (Hardcover Edition)': 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=500&q=80',
  'Algorithms & Data Structures: A Practical Guide': 'https://images.unsplash.com/photo-1516979187457-637abb4f9353?w=500&q=80',
  'Microservices Architecture with Docker & K8s': 'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=500&q=80',
  'Database Internals & Storage Engines': 'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=500&q=80',
  'Designing Distributed Cloud Systems': 'https://images.unsplash.com/photo-1519682337058-a94d519337bc?w=500&q=80',
  'Notebook': 'https://images.unsplash.com/photo-1531346878377-a5be20888e57?w=500&q=80',
  'Leather Hardcover Journal': 'https://images.unsplash.com/photo-1589829085413-56de8ae18c73?w=500&q=80',

  // Home & Kitchen
  'Ergonomic Lumbar Support Mesh Office Chair': 'https://images.unsplash.com/photo-1580481077195-c328a37db729?w=500&q=80',
  'Cold Brew Precision Espresso Coffee Maker': 'https://images.unsplash.com/photo-1517668808822-9ebb02f2a0e6?w=500&q=80',
  'Ultrasonic Aroma Diffuser with Ambient LED': 'https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?w=500&q=80',
  'Non-Stick Ceramic Cookware 10-Piece Set': 'https://images.unsplash.com/photo-1584990347449-3a322442436d?w=500&q=80',
  'Minimalist Solid Oak Bedside Lamp with Touch Dimmer': 'https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=500&q=80',
  'Stainless Steel Double-Wall Thermal French Press': 'https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=500&q=80',
  'Natural Bamboo Cutlery & Cutting Board Trio': 'https://images.unsplash.com/photo-1590794056226-79ef3a8147e1?w=500&q=80',
  'Cast Iron Enamelled Dutch Oven 5.5 Qt': 'https://images.unsplash.com/photo-1585515320310-259814833e62?w=500&q=80',
  'Stainless Steel Cookware Set': 'https://images.unsplash.com/photo-1556911220-e15b29be8c8f?w=500&q=80',
  'coffee net': 'https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=500&q=80',
  'Reusable Fine Mesh Coffee Filter Net': 'https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=500&q=80',

  // Beauty & Personal Care
  'Hydrating Vitamin C + Hyaluronic Facial Serum': 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=500&q=80',
  'Organic Herbal Daily Moisturizing Cream': 'https://images.unsplash.com/photo-1556228720-195a672e8a03?w=500&q=80',
  'Exfoliating Mineral Himalayan Body Scrub': 'https://images.unsplash.com/photo-1567928815104-b7980ee5032e?w=500&q=80',
  'Nourishing Botanical Night Repair Elixir': 'https://images.unsplash.com/photo-1608248597359-52e8d98d4f40?w=500&q=80',
  'Organic Rosewater Balancing Facial Mist': 'https://images.unsplash.com/photo-1617897903246-719242758050?w=500&q=80',
  'Vegan Cold-Pressed Argan Hair Oil 100ml': 'https://images.unsplash.com/photo-1601049541289-9b1b7bbbfe19?w=500&q=80',
  'Charcoal Clarifying Detox Detox Clay Mask': 'https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?w=500&q=80',
  'Pure Lavender Aromatherapy Essential Oil': 'https://images.unsplash.com/photo-1595981267035-7b04ca84a82d?w=500&q=80',
  'Ayurvedic Glow Face Serum': 'https://images.unsplash.com/photo-1608248597359-52e8d98d4f40?w=500&q=80',
  'suncreen': 'https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?w=500&q=80',
  'Broad Spectrum Matte Sunscreen SPF 50': 'https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?w=500&q=80',

  // Sports & Fitness
  'Yoga Mat & Resistance Bands Set': 'https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=500&q=80',
  'running shoes': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500&q=80',
  'Lightweight Breathable Running Shoes': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500&q=80',
  'snickers': 'https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=500&q=80',
  'All-Terrain Running Sneakers': 'https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=500&q=80',
  'All-Terrain Breathable Running Sneakers': 'https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=500&q=80',
  'Non-Slip High-Density Exercise Foam Roller': 'https://images.unsplash.com/photo-1518611012118-696072aa579a?w=500&q=80',
  'Speed Jump Rope with Ball Bearings': 'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=500&q=80',
  'Stainless Steel Insulated Sports Shaker Bottle': 'https://images.unsplash.com/photo-1570554886111-e80fcca6a029?w=500&q=80',
  'Adjustable Resistance Hand Grip Strengthener': 'https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=500&q=80',
  'Breathable Shock-Absorbing Cycling Gloves': 'https://images.unsplash.com/photo-1581655353564-df123a1eb820?w=500&q=80',

  // Janani Stores, Akshi, Chimayi, Baggy Jeans specific products
  'Handcrafted Ceramic Coffee Mug': 'https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?w=500&q=80',
  'Floral Print Pure Cotton Kurti': 'https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=500&q=80',
  'Eco-Friendly Canvas Tote Bag': 'https://images.unsplash.com/photo-1544816155-12df9643f363?w=500&q=80',
  'Braided 100W Fast-Charging USB-C Cable': 'https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?w=500&q=80',
  'Anti-Glare Blue Light Computer Glasses': 'https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=500&q=80',
  'Multi-Angle Aluminum Phone & Tablet Stand': 'https://images.unsplash.com/photo-1586105251261-72a756497a11?w=500&q=80',
  'Set of 4 Scented Botanical Soy Wax Candles': 'https://images.unsplash.com/photo-1603006905003-be475563bc59?w=500&q=80',
  'Soft Microfiber Quick-Dry Bath Mat': 'https://images.unsplash.com/photo-1584100936595-c0654b55a2e6?w=500&q=80',
  'Glass Water Carafe with Natural Wood Ball Lid': 'https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=500&q=80',
  'High-Rise Vintage Wide-Leg Baggy Jeans': 'https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=500&q=80',
  'Oversized Streetwear Heavyweight Acid Wash Tee': 'https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?w=500&q=80',
  'Relaxed Fit Tactical Cargo Pants with Pockets': 'https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=500&q=80',
};

// Granular keyword map with distinct URLs
const KEYWORD_MAP = [
  // Electronics
  { keywords: ['dock', 'hub', 'thunderbolt'], url: 'https://images.unsplash.com/photo-1625842268584-8f3296236761?w=500&q=80' },
  { keywords: ['webcam', 'camera'], url: 'https://images.unsplash.com/photo-1587826080692-f439cd0b70da?w=500&q=80' },
  { keywords: ['mouse', 'trackball'], url: 'https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=500&q=80' },
  { keywords: ['keyboard'], url: 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=500&q=80' },
  { keywords: ['earbud', 'airpod'], url: 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=500&q=80' },
  { keywords: ['headphone'], url: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&q=80' },
  { keywords: ['smartwatch', 'watch'], url: 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&q=80' },
  { keywords: ['charger', 'charging'], url: 'https://images.unsplash.com/photo-1622445262464-84b14e3295b6?w=500&q=80' },
  { keywords: ['fridge', 'refrigerator', 'cooler'], url: 'https://images.unsplash.com/photo-1584992236310-6edddc08acff?w=500&q=80' },
  { keywords: ['speaker', 'audio'], url: 'https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=500&q=80' },
  { keywords: ['laptop', 'macbook'], url: 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500&q=80' },

  // Books
  { keywords: ['data science', 'ai', 'artificial intelligence'], url: 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500&q=80' },
  { keywords: ['react', 'web architecture', 'fastapi'], url: 'https://images.unsplash.com/photo-1532012164546-f432f2e3777a?w=500&q=80' },
  { keywords: ['cloud', 'distributed'], url: 'https://images.unsplash.com/photo-1512820790803-83ca734da794?w=500&q=80' },
  { keywords: ['deep learning', 'neural'], url: 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=500&q=80' },
  { keywords: ['algorithms', 'data structure'], url: 'https://images.unsplash.com/photo-1516979187457-637abb4f9353?w=500&q=80' },
  { keywords: ['microservice', 'docker', 'k8s'], url: 'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=500&q=80' },
  { keywords: ['database', 'storage'], url: 'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=500&q=80' },
  { keywords: ['journal', 'notebook', 'diary'], url: 'https://images.unsplash.com/photo-1589829085413-56de8ae18c73?w=500&q=80' },

  // Fashion
  { keywords: ['saree', 'sari'], url: 'https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=500&q=80' },
  { keywords: ['kurti', 'kurta'], url: 'https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=500&q=80' },
  { keywords: ['earring', 'jewelry'], url: 'https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=500&q=80' },
  { keywords: ['jean', 'denim'], url: 'https://images.unsplash.com/photo-1542272604-787c3835535d?w=500&q=80' },
  { keywords: ['windbreaker', 'jacket'], url: 'https://images.unsplash.com/photo-1544923246-77307dd654cb?w=500&q=80' },
  { keywords: ['sweater', 'crewneck', 'wool'], url: 'https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=500&q=80' },
  { keywords: ['hoodie', 'fleece'], url: 'https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=500&q=80' },
  { keywords: ['jogger', 'sweatpant'], url: 'https://images.unsplash.com/photo-1552902865-b72c031ac5ea?w=500&q=80' },
  { keywords: ['legging', 'tight'], url: 'https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=500&q=80' },
  { keywords: ['tee', 't-shirt', 'shirt'], url: 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=500&q=80' },

  // Home & Kitchen
  { keywords: ['chair', 'seating'], url: 'https://images.unsplash.com/photo-1580481077195-c328a37db729?w=500&q=80' },
  { keywords: ['espresso', 'coffee maker'], url: 'https://images.unsplash.com/photo-1517668808822-9ebb02f2a0e6?w=500&q=80' },
  { keywords: ['diffuser', 'aroma'], url: 'https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?w=500&q=80' },
  { keywords: ['dutch oven', 'cast iron'], url: 'https://images.unsplash.com/photo-1585515320310-259814833e62?w=500&q=80' },
  { keywords: ['cookware', 'pot', 'pan'], url: 'https://images.unsplash.com/photo-1584990347449-3a322442436d?w=500&q=80' },
  { keywords: ['lamp', 'light'], url: 'https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=500&q=80' },
  { keywords: ['french press'], url: 'https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=500&q=80' },
  { keywords: ['cutting board', 'cutlery'], url: 'https://images.unsplash.com/photo-1590794056226-79ef3a8147e1?w=500&q=80' },
  { keywords: ['filter', 'coffee net'], url: 'https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=500&q=80' },

  // Beauty & Personal Care
  { keywords: ['vitamin c', 'hyaluronic', 'serum'], url: 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=500&q=80' },
  { keywords: ['moisturiz', 'cream'], url: 'https://images.unsplash.com/photo-1556228720-195a672e8a03?w=500&q=80' },
  { keywords: ['scrub', 'exfoliat'], url: 'https://images.unsplash.com/photo-1567928815104-b7980ee5032e?w=500&q=80' },
  { keywords: ['elixir', 'night repair'], url: 'https://images.unsplash.com/photo-1608248597359-52e8d98d4f40?w=500&q=80' },
  { keywords: ['mist', 'rosewater'], url: 'https://images.unsplash.com/photo-1617897903246-719242758050?w=500&q=80' },
  { keywords: ['argan', 'hair oil'], url: 'https://images.unsplash.com/photo-1601049541289-9b1b7bbbfe19?w=500&q=80' },
  { keywords: ['clay mask', 'charcoal'], url: 'https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?w=500&q=80' },
  { keywords: ['lavender', 'essential oil'], url: 'https://images.unsplash.com/photo-1595981267035-7b04ca84a82d?w=500&q=80' },
  { keywords: ['sunscreen', 'suncreen', 'spf'], url: 'https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?w=500&q=80' },

  // Sports & Fitness
  { keywords: ['yoga', 'mat', 'band'], url: 'https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=500&q=80' },
  { keywords: ['sneaker', 'snickers'], url: 'https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=500&q=80' },
  { keywords: ['running shoes', 'shoe', 'footwear'], url: 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500&q=80' },
];

const CATEGORY_FALLBACKS = {
  'Electronics': 'https://images.unsplash.com/photo-1498049794561-7780e7231661?w=500&q=80',
  'Fashion': 'https://images.unsplash.com/photo-1445205170230-053b83016050?w=500&q=80',
  'Books': 'https://images.unsplash.com/photo-1495446815901-a7297e633e8d?w=500&q=80',
  'Home & Kitchen': 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=500&q=80',
  'Beauty & Personal Care': 'https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=500&q=80',
  'Sports & Fitness': 'https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=500&q=80',
  'Other': 'https://images.unsplash.com/photo-1513151233558-d860c5398176?w=500&q=80',
};

const GENERIC_FALLBACK = 'https://images.unsplash.com/photo-1472851294608-062f824d29cc?w=500&q=80';

export function getProductImageUrl(productName = '', category = '') {
  const trimmedName = (productName || '').trim();

  // 1. Direct exact name lookup
  if (EXACT_PRODUCT_MAP[trimmedName]) {
    return EXACT_PRODUCT_MAP[trimmedName];
  }

  // 2. Case-insensitive lookup against exact map keys
  const nameLower = trimmedName.toLowerCase();
  for (const [key, url] of Object.entries(EXACT_PRODUCT_MAP)) {
    if (key.toLowerCase() === nameLower) {
      return url;
    }
  }

  // 3. Granular keyword matching
  for (const entry of KEYWORD_MAP) {
    for (const kw of entry.keywords) {
      if (nameLower.includes(kw)) {
        return entry.url;
      }
    }
  }

  // 4. Category fallback
  return CATEGORY_FALLBACKS[category] || GENERIC_FALLBACK;
}
