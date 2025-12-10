-- Migration: Seed initial product categories
-- Seeds 79 categories across PC components, home appliances, electronics, and more

-- Up
INSERT INTO categories (name, slug, description) VALUES
    -- PC Components
    ('Motherboards', 'motherboard', 'Computer motherboards and mainboards'),
    ('CPUs', 'cpu', 'Computer processors'),
    ('GPUs', 'gpu', 'Graphics cards and video cards'),
    ('RAM', 'ram', 'Computer memory modules'),
    ('Storage', 'storage', 'SSDs, HDDs, and storage devices'),
    ('Cases', 'case', 'Computer cases and chassis'),
    ('Power Supplies', 'psu', 'Power supply units'),
    ('Cooling', 'cooling', 'Fans, liquid cooling, and thermal solutions'),
    ('Monitors', 'monitor', 'Computer monitors and displays'),

    -- Peripherals
    ('Keyboards', 'keyboard', 'Computer keyboards'),
    ('Mice', 'mouse', 'Computer mice and pointing devices'),
    ('Headsets', 'headset', 'Headphones and gaming headsets'),
    ('Speakers', 'speaker', 'Computer speakers and audio systems'),
    ('Webcams', 'webcam', 'Web cameras'),

    -- Networking
    ('Routers', 'router', 'Network routers'),
    ('Network Cards', 'network-card', 'Network interface cards'),

    -- Home Appliances - Major Appliances
    ('Refrigerators', 'refrigerator', 'Refrigerators and freezers'),
    ('Washing Machines', 'washing-machine', 'Washing machines'),
    ('Dryers', 'dryer', 'Clothes dryers'),
    ('Dishwashers', 'dishwasher', 'Dishwashing machines'),
    ('Ovens', 'oven', 'Ovens and ranges'),
    ('Stoves', 'stove', 'Cooking stoves and cooktops'),
    ('Range Hoods', 'range-hood', 'Kitchen exhaust hoods'),

    -- Home Appliances - Kitchen Small Appliances
    ('Microwaves', 'microwave', 'Microwave ovens'),
    ('Coffee Makers', 'coffee-maker', 'Coffee machines'),
    ('Blenders', 'blender', 'Blenders and food processors'),
    ('Toasters', 'toaster', 'Toasters and toaster ovens'),
    ('Food Processors', 'food-processor', 'Food processors'),
    ('Electric Kettles', 'electric-kettle', 'Electric water kettles'),
    ('Slow Cookers', 'slow-cooker', 'Slow cookers and crock pots'),
    ('Air Fryers', 'air-fryer', 'Air fryers'),
    ('Mixers', 'mixer', 'Stand mixers and hand mixers'),
    ('Juicers', 'juicer', 'Juice extractors'),
    ('Rice Cookers', 'rice-cooker', 'Rice cookers'),

    -- Home Appliances - Cleaning
    ('Vacuum Cleaners', 'vacuum-cleaner', 'Vacuum cleaners'),
    ('Robot Vacuums', 'robot-vacuum', 'Robotic vacuum cleaners'),
    ('Steam Cleaners', 'steam-cleaner', 'Steam cleaning machines'),
    ('Irons', 'iron', 'Clothing irons and steamers'),

    -- Home Appliances - Climate Control
    ('Air Conditioners', 'air-conditioner', 'Air conditioning units'),
    ('Fans', 'fan', 'Electric fans and tower fans'),
    ('Heaters', 'heater', 'Space heaters'),
    ('Dehumidifiers', 'dehumidifier', 'Dehumidifying units'),
    ('Humidifiers', 'humidifier', 'Air humidifiers'),
    ('Air Purifiers', 'air-purifier', 'Air purification systems'),

    -- Home Appliances - Water Systems
    ('Water Heaters', 'water-heater', 'Water heating systems'),
    ('Water Purifiers', 'water-purifier', 'Water filtration systems'),
    ('Water Dispensers', 'water-dispenser', 'Water coolers and dispensers'),

    -- Personal Care Appliances
    ('Hair Dryers', 'hair-dryer', 'Hair dryers and blow dryers'),
    ('Hair Straighteners', 'hair-straightener', 'Hair straighteners and flat irons'),
    ('Hair Curlers', 'hair-curler', 'Hair curling irons and curlers'),
    ('Electric Shavers', 'electric-shaver', 'Electric shavers and trimmers'),
    ('Electric Toothbrushes', 'electric-toothbrush', 'Electric toothbrushes'),

    -- Electronics & Entertainment
    ('TVs', 'tv', 'Televisions and displays'),
    ('Soundbars', 'soundbar', 'Soundbars and home theater audio'),
    ('Projectors', 'projector', 'Video projectors'),
    ('Streaming Devices', 'streaming-device', 'TV streaming devices'),
    ('Gaming Consoles', 'gaming-console', 'Video game consoles'),

    -- Smart Home & Security
    ('Smart Speakers', 'smart-speaker', 'Smart speakers and voice assistants'),
    ('Security Cameras', 'security-camera', 'Home security cameras'),
    ('Video Doorbells', 'video-doorbell', 'Smart video doorbells'),
    ('Smart Locks', 'smart-lock', 'Smart door locks'),
    ('Smart Thermostats', 'smart-thermostat', 'Smart thermostats'),
    ('Smart Lighting', 'smart-lighting', 'Smart light bulbs and systems'),

    -- Mobile & Tablets
    ('Smartphones', 'smartphone', 'Mobile phones'),
    ('Tablets', 'tablet', 'Tablet computers'),
    ('Smartwatches', 'smartwatch', 'Smart watches and fitness trackers'),
    ('E-Readers', 'e-reader', 'Electronic book readers'),

    -- Laptops & Computers
    ('Laptops', 'laptop', 'Laptop computers'),
    ('Desktops', 'desktop', 'Desktop computers'),
    ('Mini PCs', 'mini-pc', 'Mini and compact PCs'),
    ('Chromebooks', 'chromebook', 'Chromebook laptops')
ON CONFLICT (slug) DO NOTHING;

-- Down
-- Remove all seeded categories
DELETE FROM categories WHERE slug IN (
    'motherboard', 'cpu', 'gpu', 'ram', 'storage', 'case', 'psu', 'cooling', 'monitor',
    'keyboard', 'mouse', 'headset', 'speaker', 'webcam',
    'router', 'network-card',
    'refrigerator', 'washing-machine', 'dryer', 'dishwasher', 'oven', 'stove', 'range-hood',
    'microwave', 'coffee-maker', 'blender', 'toaster', 'food-processor', 'electric-kettle',
    'slow-cooker', 'air-fryer', 'mixer', 'juicer', 'rice-cooker',
    'vacuum-cleaner', 'robot-vacuum', 'steam-cleaner', 'iron',
    'air-conditioner', 'fan', 'heater', 'dehumidifier', 'humidifier', 'air-purifier',
    'water-heater', 'water-purifier', 'water-dispenser',
    'hair-dryer', 'hair-straightener', 'hair-curler', 'electric-shaver', 'electric-toothbrush',
    'tv', 'soundbar', 'projector', 'streaming-device', 'gaming-console',
    'smart-speaker', 'security-camera', 'video-doorbell', 'smart-lock', 'smart-thermostat', 'smart-lighting',
    'smartphone', 'tablet', 'smartwatch', 'e-reader',
    'laptop', 'desktop', 'mini-pc', 'chromebook'
);
