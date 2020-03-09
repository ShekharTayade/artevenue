CREATE OR REPLACE VIEW wishlist_item_view AS
	SELECT 	"wishlist_item_id", "wishlist_id", b."stock_image_id" as "product_id", "promotion_id", "quantity", "item_unit_price", "item_sub_total",
		"item_disc_amt", "item_tax", "item_total", "moulding_id", "moulding_size", "print_medium_id", 
		"print_medium_size", "mount_id", "mount_size", "board_id", "board_size", "acrylic_id",
		"acrylic_size", "stretch_id", "stretch_size", "image_width", "image_height", "created_date",
		"updated_date", 'STOCK-IMAGE' as product_type_id,
		"user_collection_id", "user_space_id"
	FROM "artevenue_wishlist_stock_image" b
	
	UNION

	SELECT 	"wishlist_item_id", "wishlist_id", b."user_image_id" as "product_id", "promotion_id", "quantity", "item_unit_price", "item_sub_total",
		"item_disc_amt", "item_tax", "item_total", "moulding_id", "moulding_size", "print_medium_id", 
		"print_medium_size", "mount_id", "mount_size", "board_id", "board_size", "acrylic_id",
		"acrylic_size", "stretch_id", "stretch_size", "image_width", "image_height", "created_date",
		"updated_date", 'USER-IMAGE' as product_type_id,
		"user_collection_id", "user_space_id"
	FROM "artevenue_wishlist_user_image" b
	
	UNION
	
	SELECT 	"wishlist_item_id", "wishlist_id", b."stock_collage_id" as "product_id", "promotion_id", "quantity", "item_unit_price", "item_sub_total",
		"item_disc_amt", "item_tax", "item_total", "moulding_id", "moulding_size", "print_medium_id", 
		"print_medium_size", "mount_id", "mount_size", "board_id", "board_size", "acrylic_id",
		"acrylic_size", "stretch_id", "stretch_size", "image_width", "image_height", "created_date",
		"updated_date", 'STOCK-COLLAGE' as product_type_id,
		"user_collection_id", "user_space_id"
	FROM "artevenue_wishlist_stock_collage" b
	
	UNION
	SELECT 	"wishlist_item_id", "wishlist_id", b."original_art_id" as "product_id", "promotion_id", "quantity", "item_unit_price", "item_sub_total",
		"item_disc_amt", "item_tax", "item_total", "moulding_id", "moulding_size", "print_medium_id", 
		"print_medium_size", "mount_id", "mount_size", "board_id", "board_size", "acrylic_id",
		"acrylic_size", "stretch_id", "stretch_size", "image_width", "image_height", "created_date",
		"updated_date", 'ORIGINAL-ART' as product_type_id,
		"user_collection_id", "user_space_id"
	FROM "artevenue_wishlist_original_art" b