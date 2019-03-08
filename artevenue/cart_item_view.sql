CREATE OR REPLACE VIEW cart_item_view AS
	SELECT 	"cart_item_id", "cart_id", "promotion_id", "quantity", "item_unit_price", "item_sub_total",
		"item_disc_amt", "item_tax", "item_total", "moulding_id", "moulding_size", "print_medium_id", 
		"print_medium_size", "mount_id", "mount_size", "board_id", "board_size", "acrylic_id",
		"acrylic_size", "stretch_id", "stretch_size", "image_width", "image_height", "created_date",
		"updated_date", b."stock_image_id" as product_id
	FROM "artevenue_cart_item", "artevenue_cart_stock_image" b
	WHERE "artevenue_cart_item"."cart_item_id" = b.cart_item_ptr_id
	
	UNION

	SELECT 	"cart_item_id", "cart_id", "promotion_id", "quantity", "item_unit_price", "item_sub_total",
		"item_disc_amt", "item_tax", "item_total", "moulding_id", "moulding_size", "print_medium_id", 
		"print_medium_size", "mount_id", "mount_size", "board_id", "board_size", "acrylic_id",
		"acrylic_size", "stretch_id", "stretch_size", "image_width", "image_height", "created_date",
		"updated_date", b."user_image_id" as product_id
	FROM "artevenue_cart_item", "artevenue_cart_user_image" b
	WHERE "artevenue_cart_item"."cart_item_id" = b.cart_item_ptr_id
	
	UNION
	
	SELECT 	"cart_item_id", "cart_id", "promotion_id", "quantity", "item_unit_price", "item_sub_total",
		"item_disc_amt", "item_tax", "item_total", "moulding_id", "moulding_size", "print_medium_id", 
		"print_medium_size", "mount_id", "mount_size", "board_id", "board_size", "acrylic_id",
		"acrylic_size", "stretch_id", "stretch_size", "image_width", "image_height", "created_date",
		"updated_date", b."stock_collage_id" as product_id
	FROM "artevenue_cart_item", "artevenue_cart_stock_collage" b
	WHERE "artevenue_cart_item"."cart_item_id" = b.cart_item_ptr_id
	
	UNION
	SELECT 	"cart_item_id", "cart_id", "promotion_id", "quantity", "item_unit_price", "item_sub_total",
		"item_disc_amt", "item_tax", "item_total", "moulding_id", "moulding_size", "print_medium_id", 
		"print_medium_size", "mount_id", "mount_size", "board_id", "board_size", "acrylic_id",
		"acrylic_size", "stretch_id", "stretch_size", "image_width", "image_height", "created_date",
		"updated_date", b."original_art_id" as product_id
	FROM "artevenue_cart_item", "artevenue_cart_original_art" b
	WHERE "artevenue_cart_item"."cart_item_id" = b.cart_item_ptr_id
	


	
	

