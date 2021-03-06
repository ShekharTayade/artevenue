CREATE OR REPLACE VIEW product_view AS
SELECT "store_id" as store_id, "product_id" as product_id, "name" as name, "description" as description,
	"price" as price, "available_on" as available_on, "updated_at" as updated_at,
	"part_number" as part_number, "product_type_id" as product_type_id, "is_published" as is_published,  
	"seo_description" as seo_description, "seo_title" as seo_title, "charge_taxes" as charge_taxes, 
	"featured" as featured, "has_variants" as has_variants, "aspect_ratio" as aspect_ratio, 
	"image_type" as image_type, "orientation" as orientation, "max_width" as max_width,
	"max_height" as max_height, "min_width" as min_width, "publisher" as publisher, "artist" as artist,
	"colors" as colors, "key_words" as key_words, "url" as url, "thumbnail_url" as thumbnail_url,
	'' as session_id, 0 as user_id, '' as image_to_frame, '' as status, CURRENT_DATE as created_date, 
	CURRENT_DATE as updated_date, 0 as collage_layout_id, ''  as image_to_frame_thumbnail,
	0 as art_width , 0 as art_height, '' as art_medium, '' as art_surface, '' as art_surface_desc,
	'' as high_resolution_url, "category_disp_priority" as category_disp_priority,
	true as art_print_allowed,
	0 as original_art_price, 
	0 as available_qty,	
	0 as sold_qty,	
	0 as stock_image_id
FROM "artevenue_stock_image"

UNION

SELECT 0 as store_id, "product_id" as product_id, '' as name, '' as description, 
	0 as price, CURRENT_DATE as available_on, CURRENT_DATE as updated_at, '' as part_number, "product_type_id" as product_type_id, 
	'true' as is_published, '' as seo_description, '' as seo_title, 'false' as charge_taxes, 'false' as featured, 
	'false' as has_variants, 0.0 as aspect_ratio, '' as image_type, '' as orientation, 0 as max_width, 
	0 as max_height, 0 as min_width, '' as publisher, '' as artist, '' as colors, '' as key_words, 
	'' as url, '' as thumbnail_url, "session_id" as session_id, "user_id" as user, 
	"image_to_frame" as image_to_frame, "status" as status, "created_date" as created_date, 
	"updated_date" as updated_date, 0 as collage_layout_id,
	"image_to_frame_thumbnail" as image_to_frame_thumbnail,
	0 as art_width , 0 as art_height, '' as art_medium, '' as art_surface, '' as art_surface_desc,
	'' as high_resolution_url, "category_disp_priority" as category_disp_priority,
	true as art_print_allowed,
	0 as original_art_price, 
	0 as available_qty,	
	0 as sold_qty,	
	0 as stock_image_id
FROM "artevenue_user_image"

UNION
SELECT 0 as store_id, "product_id" as product_id, "name" as name, '' as description, 
	"price" as price, CURRENT_DATE as available_on, CURRENT_DATE as updated_at, '' as part_number, "product_type_id" as product_type_id, 
	"is_published" as is_published, '' as seo_description, '' as seo_title, 'false' as charge_taxes, 'false' as featured, 
	'false' as has_variants, "aspect_ratio" as aspect_ratio, '' as image_type, "orientation" as orientation, "max_width" as max_width, 
	"max_height" as max_height, "min_width" as min_width, '' as publisher, '' as artist, "colors" as colors, "key_words" as key_words, 
	"url" as url, "thumbnail_url" as thumbnail_url, '' as session_id, 0 as user, 
	'' as image_to_frame, '' as status, CURRENT_DATE as created_date, 
	CURRENT_DATE as updated_date, "collage_layout_id" as collage_layout_id,
	''  as image_to_frame_thumbnail,
	0 as art_width , 0 as art_height, '' as art_medium, '' as art_surface, '' as art_surface_desc,
	'' as high_resolution_url, "category_disp_priority" as category_disp_priority,
	true as art_print_allowed,
	0 as original_art_price, 
	0 as available_qty,	
	0 as sold_qty,	
	0 as stock_image_id
FROM "artevenue_stock_collage"

UNION
SELECT 0 as store_id, "product_id" as product_id, "name" as name, "description" as description,
	"price" as price, "available_on" as available_on, CURRENT_DATE as updated_at,
	"part_number" as part_number, "product_type_id" as product_type_id, "is_published" as is_published,  
	"seo_description" as seo_description, "seo_title" as seo_title, "charge_taxes" as charge_taxes, 
	"featured" as featured, "has_variants" as has_variants, "aspect_ratio" as aspect_ratio, 
	"image_type" as image_type, "orientation" as orientation, "max_width" as max_width,
	"max_height" as max_height, "min_width" as min_width, "publisher" as publisher, "artist" as artist,
	"colors" as colors, "key_words" as key_words, "url" as url, "thumbnail_url" as thumbnail_url,
	'' as session_id, 0 as user_id, '' as image_to_frame, '' as status, CURRENT_DATE as created_date, 
	CURRENT_DATE as updated_date, 0 as collage_layout_id, ''  as image_to_frame_thumbnail,
	"art_width" as art_width , "art_height" as art_height, "art_medium" as art_medium, 
	"art_surface" as art_surface, "art_surface_desc" as art_surface_desc,
	"high_resolution_url" as high_resolution_url, "category_disp_priority" as category_disp_priority,
	"art_print_allowed" as art_print_allowed,
	"original_art_price" as original_art_price, 
	"available_qty" as available_qty,
	"sold_qty" as sold_qty,
	"stock_image_id" as stock_image_id
FROM "artevenue_original_art"
