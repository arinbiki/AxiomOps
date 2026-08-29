-- SEED: Minimal registry for test isolation
INSERT INTO assets (asset_id, resource_id, service, name, environment, criticality, data_classification, owner_email, team, escalation_email, tags, active, updated_at)
VALUES 
  ('asset-001', 'arn:aws:s3:::prod-data-lake', 'aws', 'prod-data-lake', 'production', 'high', 'pii', 'data-platform@example.com', 'Data Platform', 'ciso@example.com', '["soc2"]', true, now()),
  ('asset-002', 'arn:aws:ec2:::i-123456', 'aws', 'web-server-01', 'staging', 'medium', 'internal', 'devops@example.com', 'DevOps', 'sre@example.com', '["soc2"]', true, now()),
  ('asset-003', 'arn:aws:rds:::prod-db', 'aws', 'prod-db', 'production', 'critical', 'phi', 'dba@example.com', 'Database', 'ciso@example.com', '["hipaa"]', true, now())
ON CONFLICT (resource_id, service) DO NOTHING;

INSERT INTO controls (control_id, framework, description, default_owner_email, default_sla_hours, active, updated_at)
VALUES 
  ('CC6.6', 'SOC2', 'Encryption at rest', 'security-engineering@example.com', '{"critical":72,"high":168,"medium":720,"low":2160}', true, now()),
  ('CC7.1', 'SOC2', 'Access logging enabled', 'security-engineering@example.com', '{"critical":24,"high":72,"medium":336,"low":720}', true, now()),
  ('HIPAA-164.312', 'HIPAA', 'Audit controls', 'compliance@example.com', '{"critical":24,"high":48,"medium":168,"low":720}', true, now())
ON CONFLICT (control_id, framework) DO NOTHING;
