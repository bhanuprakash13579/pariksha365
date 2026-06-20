-- Migration: Split SSC CGL Tier 1 "Full Paper" into 4 subject sections
-- and enable has_sectional_timing = TRUE.
--
-- SSC CGL Tier 1: Q1-25 Reasoning | Q26-50 GA | Q51-75 QA | Q76-100 English
-- Each section: 15 minutes, same marks_per_question as original.

DO $$
DECLARE
    rec RECORD;
    sec_gir UUID;
    sec_ga  UUID;
    sec_qa  UUID;
    sec_eng UUID;
    mpq     FLOAT;
    cnt     INT;
BEGIN
    FOR rec IN
        SELECT ts.id AS ts_id, sec.id AS sec_id, sec.marks_per_question
        FROM test_series ts
        JOIN sections sec ON sec.test_series_id = ts.id
        JOIN exam_stages es ON es.id = ts.exam_stage_id
        JOIN subcategories sc ON sc.id = es.subcategory_id
        JOIN categories c ON c.id = sc.category_id
        WHERE c.name ILIKE '%ssc%'
          AND sc.name = 'CGL'
          AND es.name = 'Tier 1'
          AND sec.name = 'Full Paper'
        ORDER BY ts.id
    LOOP
        mpq := rec.marks_per_question;

        -- Create 4 new sections
        INSERT INTO sections (id, test_series_id, name, time_limit_minutes, marks_per_question, order_num)
        VALUES (gen_random_uuid(), rec.ts_id, 'General Intelligence & Reasoning', 15, mpq, 1)
        RETURNING id INTO sec_gir;

        INSERT INTO sections (id, test_series_id, name, time_limit_minutes, marks_per_question, order_num)
        VALUES (gen_random_uuid(), rec.ts_id, 'General Awareness', 15, mpq, 2)
        RETURNING id INTO sec_ga;

        INSERT INTO sections (id, test_series_id, name, time_limit_minutes, marks_per_question, order_num)
        VALUES (gen_random_uuid(), rec.ts_id, 'Quantitative Aptitude', 15, mpq, 3)
        RETURNING id INTO sec_qa;

        INSERT INTO sections (id, test_series_id, name, time_limit_minutes, marks_per_question, order_num)
        VALUES (gen_random_uuid(), rec.ts_id, 'English Comprehension', 15, mpq, 4)
        RETURNING id INTO sec_eng;

        -- Bulk move questions by order_num range
        UPDATE questions SET section_id = sec_gir
        WHERE section_id = rec.sec_id AND order_num BETWEEN 1 AND 25;

        UPDATE questions SET section_id = sec_ga
        WHERE section_id = rec.sec_id AND order_num BETWEEN 26 AND 50;

        UPDATE questions SET section_id = sec_qa
        WHERE section_id = rec.sec_id AND order_num BETWEEN 51 AND 75;

        UPDATE questions SET section_id = sec_eng
        WHERE section_id = rec.sec_id AND order_num BETWEEN 76 AND 999;

        -- Any remaining (null order_num, etc.) → English section
        UPDATE questions SET section_id = sec_eng
        WHERE section_id = rec.sec_id;

        -- Delete old Full Paper section
        DELETE FROM sections WHERE id = rec.sec_id;

        -- Enable sectional timing
        UPDATE test_series SET has_sectional_timing = TRUE WHERE id = rec.ts_id;

        GET DIAGNOSTICS cnt = ROW_COUNT;
        RAISE NOTICE 'Migrated test_series %', rec.ts_id;
    END LOOP;

    RAISE NOTICE 'Migration complete.';
END;
$$;

-- Verification
SELECT
    ts.title,
    ts.has_sectional_timing,
    COUNT(sec.id) AS section_count,
    SUM(sub.q_count) AS total_questions
FROM test_series ts
LEFT JOIN sections sec ON sec.test_series_id = ts.id
LEFT JOIN LATERAL (
    SELECT COUNT(*) AS q_count FROM questions WHERE section_id = sec.id
) sub ON true
JOIN exam_stages es ON es.id = ts.exam_stage_id
JOIN subcategories sc ON sc.id = es.subcategory_id
JOIN categories c ON c.id = sc.category_id
WHERE c.name ILIKE '%ssc%' AND sc.name = 'CGL' AND es.name = 'Tier 1'
GROUP BY ts.id, ts.title, ts.has_sectional_timing
ORDER BY ts.title;
