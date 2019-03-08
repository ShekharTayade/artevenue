CREATE OR REPLACE VIEW promotion_product_view AS
SELECT "id", "promotion_id" as promotion_id, "stock_image_id" as product_id
	FROM "artevenue_promotion_stock_image"

UNION
SELECT "id", "promotion_id" as promotion_id, "stock_collage_id" as product_id
	FROM "artevenue_promotion_stock_collage"

UNION
SELECT "id", "promotion_id" as promotion_id, "original_art_id" as product_id
	FROM "artevenue_promotion_original_art"
