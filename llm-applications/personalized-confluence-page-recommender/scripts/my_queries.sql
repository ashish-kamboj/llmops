select * from page_embeddings limit 5;

/*-- View Pages metadata
SELECT id, title, labels, created_at 
FROM pages 
LIMIT 10;


-- View Extracted Text
SELECT page_id, LENGTH(content_text) as text_length, LEFT(content_text, 100) as preview
FROM page_text 
LIMIT 5;

-- View Embeddings (first 2 dimensions only since 3072 is too wide to display)
SELECT 
  pe.page_id, 
  p.title,
  embedding[1:2] as embedding_first_2_dims,
  (embedding <-> embedding) as distance_check
FROM page_embeddings pe
JOIN pages p ON pe.page_id = p.id
LIMIT 5;

-- Row counts
SELECT 
  (SELECT COUNT(*) FROM pages) as pages_count,
  (SELECT COUNT(*) FROM page_text) as page_text_count,
  (SELECT COUNT(*) FROM page_embeddings) as page_embeddings_count;
*/