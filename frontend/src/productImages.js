// Maps product keywords to appropriate free image URLs
const KEYWORD_MAP = [
  // Electronics
  { keywords: ['headphone', 'earphone', 'earbud', 'airpod'], url: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=300&fit=crop' },
  { keywords: ['keyboard', 'mechanical keyboard'], url: 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=400&h=300&fit=crop' },
  { keywords: ['mouse', 'gaming mouse'], url: 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400&h=300&fit=crop' },
  { keywords: ['smartwatch', 'watch', 'wearable'], url: 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&h=300&fit=crop' },
  { keywords: ['laptop', 'notebook', 'macbook'], url: 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&h=300&fit=crop' },
  { keywords: ['phone', 'mobile', 'iphone', 'smartphone', 'android'], url: 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400&h=300&fit=crop' },
  { keywords: ['tablet', 'ipad'], url: 'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400&h=300&fit=crop' },
  { keywords: ['camera', 'dslr', 'mirrorless'], url: 'https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=400&h=300&fit=crop' },
  { keywords: ['speaker', 'bluetooth speaker', 'jbl'], url: 'https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=400&h=300&fit=crop' },
  { keywords: ['monitor', 'display', 'screen'], url: 'https://images.unsplash.com/photo-1587202372634-32705e3bf49c?w=400&h=300&fit=crop' },
  { keywords: ['charger', 'power bank', 'cable'], url: 'https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?w=400&h=300&fit=crop' },
  { keywords: ['game', 'gaming', 'console', 'playstation', 'xbox'], url: 'https://images.unsplash.com/photo-1593118247619-e2d6f056869e?w=400&h=300&fit=crop' },
  // Fashion
  { keywords: ['shirt', 't-shirt', 'tshirt', 'polo'], url: 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&h=300&fit=crop' },
  { keywords: ['jeans', 'pant', 'trouser', 'denim'], url: 'https://images.unsplash.com/photo-1542272604-787c3835535d?w=400&h=300&fit=crop' },
  { keywords: ['shoe', 'sneaker', 'boot', 'footwear', 'sandal'], url: 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=300&fit=crop' },
  { keywords: ['dress', 'gown', 'frock'], url: 'https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=400&h=300&fit=crop' },
  { keywords: ['jacket', 'coat', 'hoodie', 'sweatshirt'], url: 'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400&h=300&fit=crop' },
  { keywords: ['bag', 'handbag', 'backpack', 'purse', 'wallet'], url: 'https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=400&h=300&fit=crop' },
  { keywords: ['sunglasses', 'glasses', 'spectacles'], url: 'https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=400&h=300&fit=crop' },
  { keywords: ['cap', 'hat', 'helmet'], url: 'https://images.unsplash.com/photo-1521369909029-2afed882baee?w=400&h=300&fit=crop' },
  // Books
  { keywords: ['book', 'novel', 'fiction', 'non-fiction', 'textbook', 'guide', 'programming', 'python', 'javascript', 'react'], url: 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=400&h=300&fit=crop' },
  // Home & Kitchen
  { keywords: ['sofa', 'couch', 'chair', 'furniture'], url: 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400&h=300&fit=crop' },
  { keywords: ['lamp', 'light', 'bulb', 'led'], url: 'https://images.unsplash.com/photo-1524484485831-a92ffc0de03f?w=400&h=300&fit=crop' },
  { keywords: ['mug', 'cup', 'coffee', 'tea'], url: 'https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?w=400&h=300&fit=crop' },
  { keywords: ['blender', 'mixer', 'juicer', 'food processor'], url: 'https://images.unsplash.com/photo-1570222094114-d054a817e56b?w=400&h=300&fit=crop' },
  { keywords: ['pan', 'pot', 'cookware', 'kitchen', 'utensil'], url: 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400&h=300&fit=crop' },
  { keywords: ['plant', 'flower', 'garden', 'succulent'], url: 'https://images.unsplash.com/photo-1493932484895-752d1471eab5?w=400&h=300&fit=crop' },
  { keywords: ['pillow', 'cushion', 'bedsheet', 'blanket', 'mattress'], url: 'https://images.unsplash.com/photo-1584100936595-c0654b55a2e6?w=400&h=300&fit=crop' },
  // Beauty
  { keywords: ['perfume', 'fragrance', 'cologne', 'deodorant'], url: 'https://images.unsplash.com/photo-1541643600914-78b084683702?w=400&h=300&fit=crop' },
  { keywords: ['lipstick', 'makeup', 'cosmetic', 'foundation', 'mascara'], url: 'https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=400&h=300&fit=crop' },
  { keywords: ['shampoo', 'conditioner', 'hair', 'lotion', 'cream', 'moisturizer', 'serum', 'skincare'], url: 'https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=400&h=300&fit=crop' },
  // Sports & Fitness
  { keywords: ['yoga', 'mat', 'pilates'], url: 'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=400&h=300&fit=crop' },
  { keywords: ['dumbbell', 'weight', 'barbell', 'gym'], url: 'https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=400&h=300&fit=crop' },
  { keywords: ['bicycle', 'cycle', 'bike'], url: 'https://images.unsplash.com/photo-1532298229144-0ec0c57515c7?w=400&h=300&fit=crop' },
  { keywords: ['football', 'soccer', 'ball', 'basketball', 'cricket', 'badminton', 'tennis'], url: 'https://images.unsplash.com/photo-1543326727-cf6c39e8f84c?w=400&h=300&fit=crop' },
  { keywords: ['treadmill', 'running', 'fitness', 'exercise'], url: 'https://images.unsplash.com/photo-1518611012118-696072aa579a?w=400&h=300&fit=crop' },
];

// Category fallback images
const CATEGORY_FALLBACKS = {
  'Electronics': 'https://images.unsplash.com/photo-1498049794561-7780e7231661?w=400&h=300&fit=crop',
  'Fashion': 'https://images.unsplash.com/photo-1445205170230-053b83016050?w=400&h=300&fit=crop',
  'Books': 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=400&h=300&fit=crop',
  'Home & Kitchen': 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400&h=300&fit=crop',
  'Beauty & Personal Care': 'https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=400&h=300&fit=crop',
  'Sports & Fitness': 'https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=400&h=300&fit=crop',
};

const GENERIC_FALLBACK = 'https://images.unsplash.com/photo-1472851294608-062f824d29cc?w=400&h=300&fit=crop';

export function getProductImageUrl(productName = '', category = '') {
  const nameLower = productName.toLowerCase();
  for (const entry of KEYWORD_MAP) {
    for (const kw of entry.keywords) {
      if (nameLower.includes(kw)) return entry.url;
    }
  }
  return CATEGORY_FALLBACKS[category] || GENERIC_FALLBACK;
}
