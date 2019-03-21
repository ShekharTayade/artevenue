CREATE OR REPLACE VIEW order_items_view AS

	SELECT "order_item_id", "order_id", "cart_item_id", "stock_image_id" as "product_id", "promotion_id", "quantity", 
		"item_unit_price", "item_sub_total", "item_disc_amt", "item_tax", "item_total", "moulding_id", "moulding_size", 
		"print_medium_id", "print_medium_size","mount_id", "mount_size", "board_id", "board_size", "acrylic_id", "acrylic_size",
		"stretch_id", "stretch_size", "image_width", "image_height", "created_date", "updated_date", 
		'STOCK-IMAGE' as product_type_id
	FROM "artevenue_order_stock_image" 
	
	UNION
	SELECT "order_item_id", "order_id", "cart_item_id", "user_image_id" as "product_id", "promotion_id", "quantity", 
		"item_unit_price", "item_sub_total", "item_disc_amt", "item_tax", "item_total", "moulding_id", "moulding_size", 
		"print_medium_id", "print_medium_size","mount_id", "mount_size", "board_id", "board_size", "acrylic_id", "acrylic_size",
		"stretch_id", "stretch_size", "image_width", "image_height", "created_date", "updated_date", 
		'USER-IMAGE' as product_type_id
	FROM "artevenue_order_user_image" 

	UNION
	SELECT "order_item_id", "order_id", "cart_item_id", "stock_collage_id" as "product_id", "promotion_id", "quantity", 
		"item_unit_price", "item_sub_total", "item_disc_amt", "item_tax", "item_total", "moulding_id", "moulding_size", 
		"print_medium_id", "print_medium_size","mount_id", "mount_size", "board_id", "board_size", "acrylic_id", "acrylic_size",
		"stretch_id", "stretch_size", "image_width", "image_height", "created_date", "updated_date", 
		'STOCK-COLLAGE' as product_type_id
	FROM "artevenue_order_stock_collage" 

	UNION
	SELECT "order_item_id", "order_id", "cart_item_id", "original_art_id" as "product_id", "promotion_id", "quantity", 
		"item_unit_price", "item_sub_total", "item_disc_amt", "item_tax", "item_total", "moulding_id", "moulding_size", 
		"print_medium_id", "print_medium_size","mount_id", "mount_size", "board_id", "board_size", "acrylic_id", "acrylic_size",
		"stretch_id", "stretch_size", "image_width", "image_height", "created_date", "updated_date", 
		'ORIGINAL-ART' as product_type_id
	FROM "artevenue_order_original_art"
	