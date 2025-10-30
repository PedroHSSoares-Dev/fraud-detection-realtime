-- Schema de transações para detecção de fraude
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    merchant_name VARCHAR(200) NOT NULL,
    merchant_category VARCHAR(50) NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_user_timestamp ON transactions(user_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_timestamp ON transactions(timestamp DESC);

-- ============================================================================
-- POPULAR BANCO COM HISTÓRICO PARA TESTES
-- ============================================================================

-- USER 1: user_normal_001 (Comportamento normal)
-- Perfil: Mora em São Paulo, gasta R$ 100-200 em supermercado/restaurante
INSERT INTO transactions (user_id, amount, merchant_name, merchant_category, latitude, longitude, timestamp) VALUES
('user_normal_001', 120.00, 'Supermercado Extra', 'grocery', -23.5505, -46.6333, NOW() - INTERVAL '7 days'),
('user_normal_001', 85.00, 'Posto Ipiranga', 'gas_station', -23.5505, -46.6333, NOW() - INTERVAL '6 days'),
('user_normal_001', 150.00, 'Restaurante Sushi', 'food', -23.5505, -46.6333, NOW() - INTERVAL '5 days'),
('user_normal_001', 95.00, 'Farmácia São Paulo', 'pharmacy', -23.5505, -46.6333, NOW() - INTERVAL '4 days'),
('user_normal_001', 200.00, 'Supermercado Carrefour', 'grocery', -23.5505, -46.6333, NOW() - INTERVAL '3 days'),
('user_normal_001', 110.00, 'Padaria Bella Vista', 'food', -23.5505, -46.6333, NOW() - INTERVAL '2 days'),
('user_normal_001', 180.00, 'Restaurante Italiano', 'food', -23.5505, -46.6333, NOW() - INTERVAL '1 day'),
('user_normal_001', 130.00, 'Supermercado Pão de Açúcar', 'grocery', -23.5505, -46.6333, NOW() - INTERVAL '12 hours');

-- USER 2: user_fraudster_001 (Histórico normal, mas vai fazer card testing)
-- Perfil: Mora em São Paulo, gasta normalmente, mas vai testar cartão
INSERT INTO transactions (user_id, amount, merchant_name, merchant_category, latitude, longitude, timestamp) VALUES
('user_fraudster_001', 100.00, 'Supermercado ABC', 'grocery', -23.5505, -46.6333, NOW() - INTERVAL '5 days'),
('user_fraudster_001', 150.00, 'Posto Shell', 'gas_station', -23.5505, -46.6333, NOW() - INTERVAL '4 days'),
('user_fraudster_001', 80.00, 'Farmácia Drogasil', 'pharmacy', -23.5505, -46.6333, NOW() - INTERVAL '3 days'),
('user_fraudster_001', 120.00, 'Restaurante', 'food', -23.5505, -46.6333, NOW() - INTERVAL '2 days');

-- USER 3: user_traveler_001 (Histórico em São Paulo, vai "viajar" para Tóquio)
-- Perfil: Mora em São Paulo, padrão de gasto normal
INSERT INTO transactions (user_id, amount, merchant_name, merchant_category, latitude, longitude, timestamp) VALUES
('user_traveler_001', 200.00, 'Restaurante Figueira Rubaiyat', 'food', -23.5505, -46.6333, NOW() - INTERVAL '6 days'),
('user_traveler_001', 150.00, 'Shopping Iguatemi', 'retail', -23.5505, -46.6333, NOW() - INTERVAL '5 days'),
('user_traveler_001', 300.00, 'Supermercado St Marche', 'grocery', -23.5505, -46.6333, NOW() - INTERVAL '4 days'),
('user_traveler_001', 180.00, 'Posto Ipiranga', 'gas_station', -23.5505, -46.6333, NOW() - INTERVAL '3 days'),
('user_traveler_001', 250.00, 'Restaurante Fasano', 'food', -23.5505, -46.6333, NOW() - INTERVAL '2 days'),
('user_traveler_001', 220.00, 'Farmácia', 'pharmacy', -23.5505, -46.6333, NOW() - INTERVAL '1 day');

-- USER 4: user_bigspender_001 (Gasta pouco normalmente, vai gastar muito)
-- Perfil: Gasta R$ 50-150 em média
INSERT INTO transactions (user_id, amount, merchant_name, merchant_category, latitude, longitude, timestamp) VALUES
('user_bigspender_001', 80.00, 'Supermercado', 'grocery', -23.5505, -46.6333, NOW() - INTERVAL '7 days'),
('user_bigspender_001', 120.00, 'Restaurante', 'food', -23.5505, -46.6333, NOW() - INTERVAL '6 days'),
('user_bigspender_001', 90.00, 'Farmácia', 'pharmacy', -23.5505, -46.6333, NOW() - INTERVAL '5 days'),
('user_bigspender_001', 110.00, 'Posto', 'gas_station', -23.5505, -46.6333, NOW() - INTERVAL '4 days'),
('user_bigspender_001', 100.00, 'Supermercado', 'grocery', -23.5505, -46.6333, NOW() - INTERVAL '3 days'),
('user_bigspender_001', 85.00, 'Padaria', 'food', -23.5505, -46.6333, NOW() - INTERVAL '2 days'),
('user_bigspender_001', 95.00, 'Restaurante', 'food', -23.5505, -46.6333, NOW() - INTERVAL '1 day');

-- USER 5: user_batch_001 e user_batch_002 (Para teste em lote)
INSERT INTO transactions (user_id, amount, merchant_name, merchant_category, latitude, longitude, timestamp) VALUES
('user_batch_001', 100.00, 'Supermercado', 'grocery', -23.5505, -46.6333, NOW() - INTERVAL '3 days'),
('user_batch_001', 150.00, 'Restaurante', 'food', -23.5505, -46.6333, NOW() - INTERVAL '2 days'),
('user_batch_002', 200.00, 'Shopping', 'retail', -23.5505, -46.6333, NOW() - INTERVAL '3 days'),
('user_batch_002', 180.00, 'Posto', 'gas_station', -23.5505, -46.6333, NOW() - INTERVAL '2 days');

-- ============================================================================
-- USUÁRIOS EXCLUSIVOS PARA DEMONSTRAÇÃO (demo_linkedin.py)
-- ============================================================================

-- USER DEMO 1: user_demo_normal (Para transação normal)
-- Perfil: Comportamento consistente em São Paulo, gasta R$ 150-250
INSERT INTO transactions (user_id, amount, merchant_name, merchant_category, latitude, longitude, timestamp) VALUES
('user_demo_normal', 180.00, 'Supermercado Zona Sul', 'grocery', -23.5505, -46.6333, NOW() - INTERVAL '10 days'),
('user_demo_normal', 200.00, 'Posto Ipiranga', 'gas_station', -23.5505, -46.6333, NOW() - INTERVAL '9 days'),
('user_demo_normal', 160.00, 'Farmácia Pague Menos', 'pharmacy', -23.5505, -46.6333, NOW() - INTERVAL '8 days'),
('user_demo_normal', 220.00, 'Restaurante Outback', 'food', -23.5505, -46.6333, NOW() - INTERVAL '7 days'),
('user_demo_normal', 190.00, 'Supermercado Extra', 'grocery', -23.5505, -46.6333, NOW() - INTERVAL '6 days'),
('user_demo_normal', 170.00, 'Padaria Bella Vista', 'food', -23.5505, -46.6333, NOW() - INTERVAL '5 days'),
('user_demo_normal', 210.00, 'Shopping Iguatemi', 'retail', -23.5505, -46.6333, NOW() - INTERVAL '4 days'),
('user_demo_normal', 185.00, 'Restaurante Figueira', 'food', -23.5505, -46.6333, NOW() - INTERVAL '3 days'),
('user_demo_normal', 195.00, 'Supermercado Carrefour', 'grocery', -23.5505, -46.6333, NOW() - INTERVAL '2 days'),
('user_demo_normal', 175.00, 'Farmácia Drogasil', 'pharmacy', -23.5505, -46.6333, NOW() - INTERVAL '1 day');

-- USER DEMO 2: user_demo_teleport (Para demonstração de teleporte)
-- Perfil: Comportamento normal em São Paulo, vai "viajar" para Tóquio
INSERT INTO transactions (user_id, amount, merchant_name, merchant_category, latitude, longitude, timestamp) VALUES
('user_demo_teleport', 250.00, 'Restaurante Jardins', 'food', -23.5505, -46.6333, NOW() - INTERVAL '8 days'),
('user_demo_teleport', 180.00, 'Supermercado', 'grocery', -23.5505, -46.6333, NOW() - INTERVAL '7 days'),
('user_demo_teleport', 220.00, 'Shopping', 'retail', -23.5505, -46.6333, NOW() - INTERVAL '6 days'),
('user_demo_teleport', 190.00, 'Posto', 'gas_station', -23.5505, -46.6333, NOW() - INTERVAL '5 days'),
('user_demo_teleport', 270.00, 'Restaurante', 'food', -23.5505, -46.6333, NOW() - INTERVAL '4 days'),
('user_demo_teleport', 200.00, 'Farmácia', 'pharmacy', -23.5505, -46.6333, NOW() - INTERVAL '3 days'),
('user_demo_teleport', 240.00, 'Restaurante Fasano', 'food', -23.5505, -46.6333, NOW() - INTERVAL '2 days'),
('user_demo_teleport', 210.00, 'Supermercado', 'grocery', -23.5505, -46.6333, NOW() - INTERVAL '1 day');

-- USER DEMO 3: user_demo_fraudster (Para demonstração de card testing)
-- Perfil: Comportamento normal, mas vai fazer card testing
INSERT INTO transactions (user_id, amount, merchant_name, merchant_category, latitude, longitude, timestamp) VALUES
('user_demo_fraudster', 150.00, 'Supermercado', 'grocery', -23.5505, -46.6333, NOW() - INTERVAL '6 days'),
('user_demo_fraudster', 180.00, 'Restaurante', 'food', -23.5505, -46.6333, NOW() - INTERVAL '5 days'),
('user_demo_fraudster', 120.00, 'Farmácia', 'pharmacy', -23.5505, -46.6333, NOW() - INTERVAL '4 days'),
('user_demo_fraudster', 160.00, 'Posto', 'gas_station', -23.5505, -46.6333, NOW() - INTERVAL '3 days'),
('user_demo_fraudster', 140.00, 'Supermercado', 'grocery', -23.5505, -46.6333, NOW() - INTERVAL '2 days');

-- Mensagem de sucesso
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Database initialized successfully!';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Tables created: transactions';
    RAISE NOTICE 'Sample users with transaction history:';
    RAISE NOTICE '  - user_normal_001: 8 transactions';
    RAISE NOTICE '  - user_fraudster_001: 4 transactions';
    RAISE NOTICE '  - user_traveler_001: 6 transactions';
    RAISE NOTICE '  - user_bigspender_001: 7 transactions';
    RAISE NOTICE '  - user_batch_001/002: 2 transactions each';
    RAISE NOTICE '========================================';
END $$;