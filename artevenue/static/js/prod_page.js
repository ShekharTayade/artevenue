
	
		var isBreakpoint = function(viewport_size){
		  //return $('.device-' + viewport_size).is(':visible');
		  if (viewport_size == 'xs'){
			return window.innerWidth < 768;
		  }
		  if (viewport_size == 'sm'){
			return window.innerWidth < 991;
		  }
		  if (viewport_size == 'md'){
			return window.innerWidth < 1199;
		  }
		  if (viewport_size == 'lg'){
			return window.innerWidth > 1199;
		  }
		}
	
		
	
		function startMagnify(){
			if (isBreakpoint('xs')==false) {
				magnify("prod-img", 3);
			}
		}
		
		function stopMagnify(){
			if (isBreakpoint('xs')==false) {
				removeGlass();
			}
		}

	
	
	
		// Global variables to store IDs of pricing components
		var product_id = '{{product.product_id}}';
		var print_medium_id = 'PAPER';
		var image_width = 8;
		var image_height = 8;
		var moulding_id = '0';
		var mount_id = '0';
		var mount_color = '0';
		var mount_size = '1'; // Default is 1 inch
		var mount_w_left, mount_w_right, mount_w_top, mount_w_bottom = '0';
		var board_id = '{{boards.board_id}}';
		var acrylic_id = '{{acrylics.acrylic_id}}';
		var stretch_id = '1'; 
		var def_mount_id = '3';	 

		var minsize = 8;
		var maxsize = 0;
		var ratio = 0;
		
		var framing_type = '';

		$body = $("body");
		
		{% if product.artist == "Huynh, Duy" %}
			minsize = 16;
		{% endif %}

		var fetch_img_on_slide = false;

		if ("{{product.aspect_ratio}}" != "NA"){
			ratio = parseFloat("{{product.aspect_ratio}}");
		}
		
		$( "#i_width" ).change(function() {
			currwidth = $(this).val();
			set_size_slider(currwidth);
			var w_cm  = parseFloat( currwidth * 2.54);
			w_cm = +w_cm.toFixed(2);
			$("#a_width_cm").html( w_cm.toString() + " cm");
		});
		$( "#i_height" ).change(function() {
			currheight = $(this).val();
			if (currheight < 8){
				currheight = 8;
			}
			currwidth = Math.round(currheight * ratio);
			set_size_slider(currwidth);
			var h_cm  = parseFloat( currheight * 2.54);
			h_cm = +h_cm.toFixed(2);
			$("#a_height_cm").html( h_cm.toString() + " cm" );
		});

		$('#no-frame').change(function () {
			if ( $(this).is(':checked') ) {
				buy_without_frame_change(true);
			} else {			
				buy_without_frame_change(false);
			}
		});

		
		/*************************/
		/* Getter setter methods */
		/*************************/		
		// Product_id
		function set_product_id (prd_id) {
			product_id = prd_id;
		}
		
		function get_product_id () {
			return product_id
		}
		
		// print_medium_id
		function set_print_medium_id (prt_med) {
			print_medium_id = prt_med;
		}
		function get_print_medium_id () {
			return print_medium_id;
		}
		
		// Image width, height
		function set_image_width(wdt) {
			image_width = wdt;
		}
		function get_image_width () {
			return image_width;
		}
		function set_image_height(hgt) {
			image_height = hgt;
		}
		function get_image_height () {
			return image_height;
		}

		//moulding_id
		function set_moulding_id(m_id) {
			moulding_id = m_id;
		}
		function get_moulding_id() {
			return moulding_id;
		}

		//mount_id
		function set_mount_id(mnt_id) {
			mount_id = mnt_id;
			{% for m in mounts %}
				if ( '{{m.mount_id}}' == mount_id ) {
					mount_color = '{{m.color}}';
				}
			{% endfor %}

		}
		function get_mount_id() {
			return mount_id;
		}

		//mount_color
		function set_mount_color(mnt_color) {
			mount_color = mnt_color;
		}
		function get_mount_color() {
			return mount_color;
		}
		
		//mount_size
		function set_mount_size(mnt_size) {
			mount_size = mnt_size;
			$("#mount-size").val(mnt_size);
		}
		function get_mount_size() {
			return mount_size;
		}
		
		//acrylic_id
		function set_acrylic_id(acr_id) {
			acrylic_id = acr_id;
		}
		function get_acrylic_id() {
			return acrylic_id;
		}

		//board_id
		function set_board_id(brd_id) {
			board_id = brd_id;
		}
		function get_board_id() {
			return board_id;
		}
		
		//stretch_id
		function set_stretch_id(strt_id) {
			stretch_id = strt_id;
		}
		function get_stretch_id() {
			return stretch_id;
		}

		function set_framing_type(typ){
			framing_type = typ;
		}

		function get_framing_type(){
			return framing_type;
		}


		function set_default_frame_mount(){
			var print_size = 10;
			if (ratio > 1){
				var hgt = 8;
				print_size = Math.round( hgt * r);
				//print_size = get_image_width();
			/*
			} else {
				print_size = get_image_height();
			*/
			}
			if ( get_print_medium_id() == 'PAPER') {				
				if (print_size <= 18) {
					set_mount_size('1');
					{% if imld_id %}
						set_moulding_id('{{imld_id}}');
					{% else %}
						set_moulding_id('18');
					{% endif %}
				} else if (print_size <= 26) {
					set_mount_size('1');
					{% if imld_id %}
						set_moulding_id('{{imld_id}}');
					{% else %}
						set_moulding_id('18');
					{% endif %}
				} else {
					set_mount_size('2');
					{% if imld_id %}
						set_moulding_id('{{imld_id}}');
					{% else %}
						set_moulding_id('24');
					{% endif %}
				}
				{% if imnt_color %}
					set_mount_color('{{imnt_color}}');
				{% else %}
					set_mount_color('#fffff0');
				{% endif %}
				
				{% if imnt_id %}
					set_mount_id('{{imnt_id');
				{% else %}
					set_mount_id('3');				
				{% endif %}
				
				set_board_id('1');
				set_acrylic_id('1');
				set_stretch_id('0');				
			} else {			
				set_mount_id('0');
				set_mount_size('1');
				set_mount_color('');
				set_board_id('0');
				set_acrylic_id('0');
				{% if imld_id %}
					set_moulding_id('{{imld_id}}');
				{% else %}
					set_moulding_id('26');
				{% endif %}
				{% if istr_id %}
					set_stretch_id('{{istr_id}}');
				{% else %}
					set_stretch_id('1');
				{% endif %}
			}
			//$("#no-frame").prop("checked", false);
		}
		
		// Set print display size
		function print_size_display(wth, hgt, framing_type=''){
			if (hgt < 4 || wth < 4){
				return;
			}
			
			switch (framing_type){
				case 'PAPER_ROLLED':
					{% for key, value in ready_prod_data_paper.items %}
						var ready_flag = true;
						if ({{value.PAPER_WIDTH_UNFRAMED}} == wth) {
							$("#paper-size-ROLLED-{{value.PAPER_WIDTH_ROLLED|floatformat}}").addClass("p_clicked");
						} else {
							$("#paper-size-ROLLED-{{value.PAPER_WIDTH_ROLLED|floatformat}}").removeClass("p_clicked");
						}
					{% endfor %}
					break;
				case 'PAPER_FRAMED_WITH_MOUNT':
					{% for key, value in ready_prod_data_paper.items %}
						var ready_flag = true;
						if ({{value.PAPER_WIDTH_UNFRAMED}} == wth) {
							$("#paper-size-FRAMED_WITH_MOUNT-{{value.PAPER_WIDTH_FRAMED_WITH_MOUNT|floatformat}}").addClass("p_clicked");
						} else {
							$("#paper-size-FRAMED_WITH_MOUNT-{{value.PAPER_WIDTH_FRAMED_WITH_MOUNT|floatformat}}").removeClass("p_clicked");
						}
					{% endfor %}
					break;
				case 'PAPER_FRAMED_WITHOUT_MOUNT':
					{% for key, value in ready_prod_data_paper.items %}
						var ready_flag = true;
						if ({{value.PAPER_WIDTH_UNFRAMED}} == wth) {
							$("#paper-size-FRAMED_WITHOUT_MOUNT-{{value.PAPER_WIDTH_FRAMED_WITHOUT_MOUNT|floatformat}}").addClass("p_clicked");
						} else {
							$("#paper-size-FRAMED_WITHOUT_MOUNT-{{value.PAPER_WIDTH_FRAMED_WITHOUT_MOUNT|floatformat}}").removeClass("p_clicked");
						}
					{% endfor %}
					break;

				case 'CANVAS_ROLLED':
					{% for key, value in ready_prod_data_canvas.items %}
						var ready_flag = true;
						if ({{value.CANVAS_WIDTH_UNFRAMED}} == wth) {
							$("#canvas-size-ROLLED-{{value.CANVAS_WIDTH_ROLLED|floatformat}}").addClass("p_clicked");
						} else {
							$("#canvas-size-ROLLED-{{value.CANVAS_WIDTH_ROLLED|floatformat}}").removeClass("p_clicked");
						}
					{% endfor %}
					break;

				case 'CANVAS_FRAMED':
					{% for key, value in ready_prod_data_canvas.items %}
						var ready_flag = true;
						if ({{value.CANVAS_WIDTH_UNFRAMED}} == wth) {
							$("#canvas-size-FRAMED-{{value.CANVAS_FRAMED_WIDTH|floatformat}}").addClass("p_clicked");
						} else {
							$("#canvas-size-FRAMED-{{value.CANVAS_FRAMED_WIDTH|floatformat}}").removeClass("p_clicked");
						}
					{% endfor %}
					break;

				case 'CANVAS_STRETCHED':
					{% for key, value in ready_prod_data_canvas.items %}
						var ready_flag = true;
						if ({{value.CANVAS_WIDTH_UNFRAMED}} == wth) {
							$("#canvas-size-STRETCHED-{{value.CANVAS_STRETCHED_WIDTH|floatformat}}").addClass("p_clicked");
						} else {
							$("#canvas-size-STRETCHED-{{value.CANVAS_STRETCHED_WIDTH|floatformat}}").removeClass("p_clicked");
						}
					{% endfor %}
					break;

				default:
					// code block
			}


			set_prod_diagram_and_frame();
			var wth_cm = wth * 2.54;
			wth_cm = +wth_cm.toFixed(2);
			var hgt_cm = hgt * 2.54;
			hgt_cm = +hgt_cm.toFixed(2);
			txt = 'Art print on ' + print_medium_id + ', Print Size: ' + wth.toString() +  ' X ' + hgt.toString() + ' inch ' + '(' + wth_cm.toString() + ' X ' + hgt_cm.toString() + ' cm )';
			$("#surface").html(print_medium_id);
			$("#print_size").html( wth.toString() +  ' X ' + hgt.toString() + ' inch ' + '(' + wth_cm.toString() + ' X ' + hgt_cm.toString() + ' cm )');
			$("#g-wrap").hide();
			var f_size = 0;
			var mnt_size = 0;
			var frame_width = image_width;
			var frame_height = image_height;
			if (moulding_id != '0' && moulding_id != ''){
				$("#frm").show();
				$("#d-frame").show();
				$("#frame-"+moulding_id).show();
				if (get_print_medium_id() == 'PAPER'){
					{% for f in paper_mouldings_show %}
						if ('{{f.moulding_id}}' == moulding_id) {			
							txt = txt + ', Frame: {{f.moulding__name}}';
							f_size = {{f.moulding__width_inner_inches}};
							var mld_wth = {{f.moulding__width_inches}};
							var mld_wth_cm = {{f.moulding__width_inches}} * 2.54;
							mld_wth_cm = +mld_wth_cm.toFixed(2);
							$("#frame_spec").html( '{{f.moulding__name}}, ' + mld_wth.toString() + ' inch (' + mld_wth_cm.toString() + ' cm)');
						}
					{% endfor %}
				} else {
					{% for f in canvas_mouldings_show %}
						if ('{{f.moulding_id}}' == moulding_id) {			
							txt = txt + ', Frame: {{f.moulding__name}}';
							f_size = {{f.moulding__width_inner_inches}};
							var mld_wth = {{f.moulding__width_inches}};
							var mld_wth_cm = {{f.moulding__width_inches}} * 2.54;
							mld_wth_cm = +mld_wth_cm.toFixed(2);
							$("#frame_spec").html('{{f.moulding__name}}' + mld_wth.toString() + ' inch ' + '(' + mld_wth_cm.toString() + ' cm)');
						}
					{% endfor %}
				}
				
				frame_width = frame_width + f_size*2;
				frame_height = frame_height + f_size*2;
				
				if (print_medium_id == 'PAPER'){
					var mnt_color = '';
					if (mount_id != '0' && mount_id != '') {
						$("#f-mnt").show();
						{% for m in mounts %}
							if ( '{{m.mount_id}}' == mount_id ) {
								mnt_color = '{{m.name|title}}';
							}
						{% endfor %}
					
						var mount_size_cm = mount_size * 2.54;
						mount_size_cm = +mount_size_cm.toFixed(2);
						txt = txt + ', ' + mount_size.toString() + ' inch (' + mount_size_cm + ' cm), ' + mnt_color + ' mount';
						$("#f_mount").html( mount_size.toString() + ' inch (' + mount_size_cm + ' cm), ' + 'Color: ' + mnt_color );
						mnt_size = parseFloat(mount_size);
						frame_width = frame_width + mnt_size*2;
						frame_height = frame_height + mnt_size*2;
					} else {
						$("#f-mnt").hide();
					}
					$(".d-acrylic").show();
				} else {
					$(".d-acrylic").hide();
					$("#d-mount").hide();
					$("#f-mnt").hide();
				}
			} else  {
				$("#frm").hide();
				$("#d-frame").hide();
				$(".d-acrylic").hide();
				$("#f-mnt").hide();
				if (get_stretch_id() == '1'){
					$("#g-wrap").show();
					txt = txt + ", Stretched Canvas";
					$("#g_wrap").html("Canvas wrapped over wooden frame at the back");
					$("d-stretch").show();
				} else {
					$("#g-wrap").hide();
					$("d-stretch").hide();
				}
			}
			
			frame_width = Math.round(frame_width);
			frame_height = Math.round(frame_height);
			var frame_width_cm = frame_width * 2.54;
			var frame_width_cm = +frame_width_cm.toFixed(2);
			frame_height_cm = frame_height * 2.54;
			frame_height_cm = +frame_height_cm.toFixed(2);
			details_txt = txt + ', Finished Size:' + frame_width.toString() +  ' X ' + frame_height.toString() + ' inch (' + frame_width_cm.toString() + ' X ' + frame_height_cm.toString() + ' cm)';
			txt = 'Finished Size: '  + frame_width.toString() +  ' X ' + frame_height.toString() + ' inch<br />' + ' FREE SHIPPING';
			$('#prod-desc').html(txt);
			$('#prod-details').html(details_txt);
			$(".fsize").html(frame_width.toString() +  ' X ' + frame_height.toString() + ' inch');
			
			if ( (get_moulding_id() == '' || get_moulding_id() == '0') && (get_stretch_id() == '0' || get_stretch_id() == '') ){
				$("#rolled").show();
			} else {
				$("#rolled").hide();
			}
			
		}
		
		/******************/
		/* Events         */
		/******************/
		function print_medium_change(prt_med, fetch_img=true, set_defaults=true, calc_cost=true){			
			set_print_medium_id(prt_med);
			var mld_id = get_moulding_id();
			var mnt_color = '';
			var mnt_size = '0';
			if (prt_med == 'PAPER') {
				if (set_defaults) {
					set_default_frame_mount(false);
				}
				$("#paper-frames").show();
				$("#canvas-frames").hide();
				$("#prod_type_paper").show();
				$("#prod_type_canvas").hide();
				mnt_color = get_mount_color();
				mnt_size = get_mount_size();
				//$("#stretched").hide();
				//$("#whatis_stretched").hide();
				$("#d-paper").show();
				$("#d-canvas").hide();
				$("#d-stretch").hide();				
				set_stretch_id('0');
				$("#m-PAPER").addClass("p_clicked");
				$("#m-CANVAS").removeClass("p_clicked");
				$("#mount-show").show();
				{% for m in mounts %}
					$("#mnt_{{m.mount_id}}").show();
				{% endfor %}
				if (mld_id != '' && mld_id !== '0'){
					set_acrylic_id('1');
					set_board_id('1');
					//set_mount_id(def_mount_id);
				}
								
			} else if (prt_med == 'CANVAS') {
					mnt_color = '';
					mnt_size = '0';
					set_mount_id('0');
					if (set_defaults) {
						set_default_frame_mount(false);
					}
					$("#paper-frames").hide();
					$("#canvas-frames").show();
					$("#prod_type_paper").hide();
					$("#prod_type_canvas").show();
					mld_id = get_moulding_id();
					$("#m-CANVAS").addClass("p_clicked");
					$("#m-PAPER").removeClass("p_clicked");
					$("#mount-show").hide();
					$("#d-paper").hide();
					$("#d-canvas").show();
					$("#f-mnt").hide();
					{% for m in mounts %}
						$("#mnt_{{m.mount_id}}").hide();
					{% endfor %}

					
				} else {
						return;
			}
			var framing_type = '';
			if (prt_med == 'PAPER'){
				$('#dropdownMenu_type_paper').prop('value', 'PAPER_FRAMED_WITH_MOUNT'); 
				$('#dropdownMenu_type_paper').text("FRAMED");
				framing_type = $("#dropdownMenu_type_paper").val();
			} else if (prt_med == 'CANVAS'){
				$('#dropdownMenu_type_canvas').prop('value', 'CANVAS_FRAMED'); 
				$('#dropdownMenu_type_canvas').text("FRAMED");
				framing_type = $("#dropdownMenu_type_canvas").val();
			}

			{% if not cart_item and not wishlist_item %}
				framing_type_chaged(prt_med, framing_type, true, false)
			{% endif %}
			//print_size_display(image_width, image_height, framing_type);

			set_max_size_with_mount(false);

			if (calc_cost) {
				calc_total_price();
			}

			if (fetch_img == true){
				$.ajax({
						url: "{% url 'get_framed_image' %}", 
						data: {'prod_id':get_product_id(), 'moulding_id': get_moulding_id(),
								'mount_color':mnt_color, 'mount_size':mnt_size, 'image_width':get_image_width(),
							'stretched_canvas': get_stretch_id()
							}, 
						dataType: 'text', 
					success: function (data) {
						document.getElementById("prod-img-card").src = "data:image/png;base64," + data;
						document.getElementById("prod-img-card-thumb").src = "data:image/png;base64," + data;
						get_cards();
					},
					error: function(xhr){
						alert("An error occured: " + xhr.status + " " + xhr.statusText); 
					}
				});
			}
		}

		function moulding_change(m_id, fetch_img = true, calc_cost=true){
			if ((m_id == '' || m_id == '0') && get_stretch_id() == '0'){
				$("#d-frame").hide();
				$("#prod-card1").hide();
				return;
			} else {
				$("#prod-card1").show();
			}
			
			$("#d-frame").show();
			set_moulding_id(m_id);
			//$('#no-frame').prop('checked', false);
			var mnt_color = '';
			var mnt_size = '0';
			
			// Add acrylic and board, or stretcher when a moulding is selected
			if (print_medium_id == 'PAPER') {
				if (m_id == '20' || m_id == '8' || m_id == '6' ) {
					if  (framing_type == 'PAPER_FRAMED_WITH_MOUNT') {
						set_mount_id('1');
						set_mount_color('#ffffff');
					}
				} else {
					mnt_color = get_mount_color();
				}
				mnt_size = get_mount_size();
				set_acrylic_id("{{acrylics.acrylic_id}}");
				set_board_id('{{boards.board_id}}');

				{% for f in paper_mouldings_show %}
					if ( {{f.moulding_id}} == m_id ) {
						$('#dropdownMenu_paper').html('{{f.moulding__name}}');
					}
				{% endfor %}

				print_size_display(image_width, image_height, $("prod_type_paper").val() );

			} else if (print_medium_id == 'CANVAS'){
				// Set the stretch by default if moulding selected on Canvas
				mnt_color = '';
				mnt_size = '0';										
				if (get_moulding_id() == '' || get_moulding_id() == '0') {
					$("#d-stretch").show();
				} else {
					$("#d-stretch").hide();
					set_stretch_id('1');
				}
				{% for f in canvas_mouldings_show %}
					if ( {{f.moulding_id}} == m_id ) {
						$('#dropdownMenu_canvas').html('{{f.moulding__name}}');
					}
				{% endfor %}
				print_size_display(image_width, image_height, $("prod_type_canvas").val() );
			}
			
		
			if (fetch_img == true){
				getFramedImg (product_id, moulding_id, mnt_color, mnt_size);
			}
			

			//print_size_display(image_width, image_height);
			set_max_size_with_mount(false);
			//Calculate the price
			if (calc_cost) {
				calc_total_price();
			}		
		}
			
		
		function mount_id_change(mnt_id, fetch_img = true, calc_cost=true ) {
			if (mnt_id == '' || mnt_id == '0'){
				return;
			}
			set_mount_id(mnt_id);
			mnt_size = $("#mount-size").val();
			if (mnt_size >= '5' || mnt_size == '' || mnt_size == '0') {
				alert("Mount size should be between 1 and 5 inch");
				return;
			}
			set_mount_size(mnt_size, false);
			if (print_medium_id == 'PAPER') {
				if (fetch_img == true){				
					getFramedImg (product_id, moulding_id, mount_color, mount_size);
				}
				if (calc_cost) {
					calc_total_price();
				}
				//print_size_display(image_width, image_height);
			}
			set_max_size_with_mount(calc_cost);
		}
		
		function mount_size_change(mnt_size, fetch_img = true, calc_cost=true ){
			if (mnt_size == '' || mnt_size == '0'){
				return;
			}
			set_mount_size(mnt_size);
			if (mnt_size >= '5' || mnt_size == '' || mnt_size == '0') {
				alert("Mount size should be between 1 and 5 inch");
				return;
			}
			if (print_medium_id == 'PAPER') {
				if (calc_cost) {
					calc_total_price();
				}
				print_size_display(image_width, image_height);
				if (fetch_img == true){
					getFramedImg (product_id, moulding_id, mount_color, mount_size);
				}
			}				
			
			var wdt = get_image_width();
			set_size_slider(wdt, calc_cost);
			//set_max_size_with_mount(calc_cost);
		}
		function stretch_changed(fetch_img = true, calc_cost=true){
			$("#d-stretch").show();
			set_stretch_id('1');
			set_moulding_id('0');			
			if (fetch_img == true){
				getFramedImg (product_id, moulding_id, mount_color, mount_size);
			}
			//print_size_display(image_width, image_height, "CANVAS_STRETCHED");
			set_max_size_with_mount(false);
			if (calc_cost) {
				calc_total_price();
			}
		}
		
		function buy_without_frame_change(yesno, fetch_img = true, calc_cost=true ){
			if (yesno == true){
				set_mount_id('0');
				set_mount_color('0');
				set_acrylic_id('0');
				set_board_id('0');
				set_moulding_id('0');
				set_mount_size('0');
				set_stretch_id('0');

				if (print_medium_id == 'CANVAS') {
					$("#whatis_stretched").show();
					$("#d-stretch").hide();	
				} else { 					
					$("#whatis_stretched").hide();
					$("#d-stretch").hide();
				}
			} else {
				set_default_frame_mount();
				if (print_medium_id == 'PAPER') {
				} else {					
					set_stretch_id('0');
					set_mount_size('0');					
				}
				
				$("#d-stretch").hide();
			}
			if (fetch_img == true){
				getFramedImg (product_id, moulding_id, mount_color, mount_size);
			}
			if (calc_cost) {
				calc_total_price();
			}
			//print_size_display(image_width, image_height);
		}
		
		function removeFrame(fetch_img = true){
			set_max_size_with_mount();
			set_moulding_id('0');
			set_mount_id('0');
			set_mount_color('');
			set_mount_size('0');
			$("#prod-card1").hide();
			$("#d-stretch").hide();	
			if (print_medium_id == 'PAPER') {
				framing_type_chaged(print_medium_id, 'PAPER_ROLLED', true)
				$("#d-stretch").hide();
				set_stretch_id('0');
			} else {
				framing_type_chaged(print_medium_id, 'CANVAS_ROLLED', true)
			}
			//$('#no-frame').prop('checked', true);
			if (fetch_img == true){
				getFramedImg (product_id, moulding_id, mount_color, mount_size);
			}
			calc_total_price();
			//print_size_display(image_width, image_height);
		}
		
		function removeMount(fetch_img = true){
			set_mount_id('0');
			set_mount_color('');
			set_mount_size(0);
			if (fetch_img == true){
				getFramedImg (product_id, moulding_id, mount_color, mount_size);
			}
			calc_total_price();
			//print_size_display(image_width, image_height);
		}

	
			
			
		jQuery(document).ready(function(){			
			$body = $("body");
			$(document).on({
				ajaxStart: function() { $body.addClass("loading");},
				ajaxStop: function() { $body.removeClass("loading");},
				//ajaxStart: function() { $("#wall-color-tool").addClass("loading");},
				//ajaxStop: function() { $("#wall-color-tool").removeClass("loading");}
				
			});

		
			$("#d-paper").hide();
			$("#d-canvas").hide();
			$("#d-frame").hide();
			$("#d-stretch").hide();
			$(".d-acrylic").hide();
		
			/*
			{% if creative_exists %}
				$("#card-slider").prepend( '<div class="card-img"> <img id = "prod-img-creative" src="{{creative_url}}" alt ="Wall Art: {{product.name}} | Room view"></div>' );
				$("#desktop-thumb").prepend('<div class = "col-2"> <img id = "card-img-creative" src="{{creative_url}}" alt ="Wall Art: {{product.name}} | Room view" class = "card-thumb" style = "max-height: 80px;"></div>')
				document.getElementById("prod-img").src = document.getElementById("prod-img-creative").src;
				$( "#card-img-creative" ).hover(function() {
					var src = document.getElementById("card-img-creative").src;
					document.getElementById("prod-img").src = src;
				});
			{% endif %}
			*/
			var w = $("#card-slider").width();
			var calc = ((w / 1 / 1) + 4).toString() + "px";
			$("#card-slider").css('min-height', calc );
			
			//min-height: calc(([slideshow width] / [slides shown]) / [image-width-to-height-ratio]) + 4px);

			
			$("#card-slider").slick({
				dots: true,
				arrows: false,
				infinite: false,
				mobileFirst: true,
				rows: 1,
				slidesToShow: 1,
				slidesToScroll: 1,
			});

			//card_html =	'<div class=" card-img"> <img id = "prod-img-creative" src="' + '/static/img/creatives/AE_Apr_17_600.jpg' + '" alt ="Wall Art: {{product.name}} | Room view"></div>';				
			//$('#card-slider').slick('slickAdd',card_html, currslide);
			//$('#card-slider').slick('slickGoTo', 1);
			
			

			$(".similar-prods-slider").slick({
				dots: true,
				infinite: true,
				mobileFirst: true,
				rows: 2,
				slidesToShow: 4,
				slidesToScroll: 4,
				responsive: [
					{
					  breakpoint: 1024,
					  settings: {
						slidesToShow: 4,
						slidesToScroll: 4,
					  }
					},
					{
					  breakpoint: 600,
					  settings: {
						slidesToShow: 3,
						slidesToScroll: 3
					  }
					},
					{
					  breakpoint: 480,
					  settings: {
						slidesToShow: 2,
						slidesToScroll: 2
					  }
					},
					{
					  breakpoint: 370,
					  settings: {
						slidesToShow: 2,
						slidesToScroll: 2
					  }
					}
				]
			});
				
			r = {{product.aspect_ratio}};
			if (r > 1) {
				ht = 8
				wd = Math.round(ht * r)
				{% if product.artist == "Huynh, Duy" %}
					ht = 16;
				{% endif %}
					
			} else {
				wd = 10
				{% if product.artist == "Huynh, Duy" %}
					wd = 16;
				{% endif %}
			}						

			{% if product %}
				set_product_id("{{product.product_id}}");
			{% endif %}	

			
			//$("#i_standard").click();

			{% if cart_item or wishlist_item %}
				set_for_cart_wishlist_item();
			{% else %}
				{% if iuser_width %}
					if ({{iuser_width}} > 0) {
						set_size_slider({{iuser_width}}, false);
						var wd = {{iuser_width}};
						set_image_width(wd);
						var ht = Math.round(get_image_width() / ratio);
						set_image_height(ht);

						$("#i_width").val(wd);
						var w_cm  = parseFloat( wd * 2.54);
						w_cm = +w_cm.toFixed(2);
						$("#a_width_cm").html( w_cm.toString() + " cm" );
						
						$("#i_height").val(ht);
						var h_cm  = parseFloat( ht * 2.54);
						h_cm = +h_cm.toFixed(2);
						$("#a_height_cm").html( h_cm.toString() + " cm" );
						
						if ('{{imld_id}}' != ''){
							moulding_change("{{imld_id}}", false, false, true);
						} else {
							set_moulding_id("0");
						}
						if ('{{isurface}}' != '' ){
							if ( '{{isurface}}' == 'CANVAS') {
								$('#mouldings_include_paper').hide(); 
								$('#mouldings_include_canvas').show();
								if ( '{{istr_id}}' != '') {
									set_stretch_id("{{istr_id}}");
									$("#d-stretch").show();
									//$("#in_stretched").prop('checked', true);
								}
							} else {
								$('#mouldings_include_paper').show(); 
								$('#mouldings_include_canvas').hide();
								{% if imnt_id %}
									mount_id_change("{{imnt_id}}", false, false);
								{% else %}
									set_mount_id("0");
								{% endif %}
								
								set_mount_color("{{imnt_color}}");	
								set_mount_size("{{imnt_size}}");							
							}							
							print_medium_change("{{isurface}}", false, false, true);
						} else {
							print_medium_change('PAPER', false, false, true);
						}
						getFramedImg (product_id, moulding_id, mount_color, mount_size);
						print_size_display(image_width, image_height)
					} else {
						if ({{product.max_width}} < wd ){
							set_size_slider({{product.max_width}}, false);
						}
						framing_type_chaged('PAPER', 'PAPER_FRAMED_WITH_MOUNT', true);
						//set_ready_product('PAPER', 'PAPER_FRAMED_WITH_MOUNT', wd, wd, ht, get_moulding_id(), get_mount_id(), get_mount_size(), get_mount_color(), get_acrylic_id(), get_board_id(), '0', true);
						print_medium_change('PAPER', false, true, false);
						//buy_without_frame_change(false, true, true);
					}
				{% else %}
					if ({{product.max_width}} < wd ){
						set_size_slider({{product.max_width}}, false);
					}
					print_medium_change('PAPER', false, true, false);
					framing_type_chaged('PAPER', 'PAPER_FRAMED_WITH_MOUNT', true);
					//buy_without_frame_change(false, true, true);
				{% endif %}
			{% endif %}			
			

			wigzo('track', 'productview', 'https://artevenue.com/art-print/{{product.product_id}}/');

			setTimeout(function(){ 
				var p_price = $("#prod-price").text();
				
				wigzo("index", {
					"canonicalUrl": "https://artevenue.com/art-print/{{product.product_id}}/",
					"title": "{{product.name}}",
					"description": "{{product.description}}",
					"price": p_price,
					"productId": "{{product.product_id}}",
					"image": "https://artevenue.com{% static product.url %}",
					"language":"en" 
				});
			
			 }, 800);
			

		});

		// Initialize tooltip component
		$(function () {
		  $('[data-toggle="tooltip"]').tooltip()
		})

		// Initialize popover component
		$(function () {
		  $('[data-toggle="popover"]').popover()
		})


	
	
	
		function set_for_cart_wishlist_item(){
			{% if cart_item %}
				set_image_width({{cart_item.image_width}});
				set_image_height({{cart_item.image_height}});
				{% if cart_item.print_medium_id %}
					set_print_medium_id("{{cart_item.print_medium_id}}");
				{% endif %}
				{% if cart_item.moulding_id %}
					moulding_change("{{cart_item.moulding_id}}", false, false);
				{% else %}
					set_moulding_id("0");
				{% endif %}
				{% if cart_item.mount_id %}
					set_mount_id("{{cart_item.mount_id}}");
					{% for m in mounts %}
						if ('{{m.mount_id}}' == '{{cart_item.mount_id}}'){
							mount_id_change("{{cart_item.mount_id}}", false, false);
						}
					{% endfor %}
				{% else %}
					set_mount_id("0");
				{% endif %}
				{% if cart_item.mount_size %}
					mount_size_change("{{cart_item.mount_size}}", false, false);
				{% else %}
					set_mount_size("0");
				{% endif %}
				{% if cart_item.acrylic_id %}
					set_acrylic_id("{{cart_item.acrylic_id}}", false, false);
				{% else %}
					set_acrylic_id("0");
				{% endif %}
				{% if cart_item.board_id %}
					set_board_id("{{cart_item.board_id}}", false, false);
				{% else %}
					set_board_id("0");					
				{% endif %}
				{% if cart_item.stretch_id %}
					set_stretch_id("{{cart_item.stretch_id}}", false, false);
				{% else %}
					set_stretch_id("0");
				{% endif %}
				
				{% if cart_item.print_medium_id %}
					print_medium_change("{{cart_item.print_medium_id}}", false, false, false);
				{% endif %}

				var typ = '';
				if ("{{cart_item.print_medium_id}}" == 'PAPER') {
					if (mount_id != '0' && mount_id != '' ) {	
						typ = 'PAPER_FRAMED_WITH_MOUNT';
					}
					if ((moulding_id != '0' && moulding_id != '') && (mount_id == '0' || mount_id == '' )) {	
						typ = 'PAPER_FRAMED_WITHOUT_MOUNT';
					}
					if (moulding_id == '0' || moulding_id == '') {	
						typ = 'PAPER_ROLLED';
					}
				} else {
					if (moulding_id != '0' || moulding_id != '') {	
						typ = 'CANVAS_FRAMED_WITH_MOUNT';
					}
					if ((moulding_id == '0' || moulding_id == '') && (stretch_id == '1' )) {	
						typ = 'CANVAS_STRETCHED';
					}
					if (moulding_id == '0' || moulding_id == '') {	
						typ = 'CANVAS_ROLLED';
					}
				}
				set_size_slider({{cart_item.image_width}}, false, typ);
				<!-- $( "#size-slider" ).slider( "option", "value", {{cart_item.image_width}}); -->
				

				framing_type_chaged("{{cart_item.print_medium_id}}", typ, false)
			{% endif %}

			{% if wishlist_item %}
				set_image_width({{wishlist_item.image_width}});
				set_image_height({{wishlist_item.image_height}});
				{% if wishlist_item.print_medium_id %}
					set_print_medium_id("{{wishlist_item.print_medium_id}}");
				{% endif %}
				{% if wishlist_item.moulding_id %}
					moulding_change("{{wishlist_item.moulding_id}}", false, false);
				{% else %}
					set_moulding_id("0");
				{% endif %}
				{% if wishlist_item.mount_id %}
					set_mount_id("{{wishlist_item.mount_id}}");
					{% for m in mounts %}
						if ('{{m.mount_id}}' == '{{wishlist_item.mount_id}}'){
							mount_id_change("{{wishlist_item.mount_id}}", false, false);
						}
					{% endfor %}
				{% else %}
					set_mount_id("0");
				{% endif %}
				{% if wishlist_item.mount_size %}
					mount_size_change("{{wishlist_item.mount_size}}", false, false);
				{% else %}
					set_mount_size("0");
				{% endif %}
				{% if wishlist_item.acrylic_id %}
					set_acrylic_id("{{wishlist_item.acrylic_id}}", false, false);
				{% else %}
					set_acrylic_id("0");
				{% endif %}
				{% if wishlist_item.board_id %}
					set_board_id("{{wishlist_item.board_id}}", false, false);
				{% else %}
					set_board_id("0");					
				{% endif %}
				{% if wishlist_item.stretch_id %}
					set_stretch_id("{{wishlist_item.stretch_id}}", false, false);
				{% else %}
					set_stretch_id("0");
				{% endif %}
				set_size_slider({{wishlist_item.image_width}}, false);
				//$( "#size-slider" ).slider( "option", "value", {{wishlist_item.image_width}});
				$("#i_width").val({{wishlist_item.image_width}});
				
				{% if wishlist_item.print_medium_id %}
					print_medium_change("{{wishlist_item.print_medium_id}}", false, false, false);
				{% endif %}

				var typ = '';
				if ("{{wishlist_item.print_medium_id}}" == 'PAPER') {
					if (mount_id != '0' && mount_id != '' ) {	
						typ = 'PAPER_FRAMED_WITH_MOUNT';
					}
					if ((moulding_id != '0' && moulding_id != '') && (mount_id == '0' || mount_id == '' )) {	
						typ = 'PAPER_FRAMED_WITHOUT_MOUNT';
					}
					if (moulding_id == '0' || moulding_id == '') {	
						typ = 'PAPER_ROLLED';
					}
				} else {
					if (moulding_id != '0' || moulding_id != '') {	
						typ = 'CANVAS_FRAMED_WITH_MOUNT';
					}
					if ((moulding_id == '0' || moulding_id == '') && (stretch_id == '1' )) {	
						typ = 'CANVAS_STRETCHED';
					}
					if (moulding_id == '0' || moulding_id == '') {	
						typ = 'CANVAS_ROLLED';
					}
				}

				framing_type_chaged("{{wishlist_item.print_medium_id}}", typ, false)

			{% endif %}
			calc_total_price();
		}
			
	

	
		function startMagnify(){
			if (isBreakpoint('xs')==false) {
				magnify("prod-img-card", 3);
			}
		}
		
		function stopMagnify(){
			if (isBreakpoint('xs')==false) {
				removeGlass();
			}
		}

		$( "#prod-img-card-thumb" ).hover(function() {
			var src = document.getElementById("prod-img-card-thumb").src;
			document.getElementById("prod-img-card").src = src;
		});
		$( "#prod-card1" ).hover(function() {
			var src = document.getElementById("prod-card1").src;
			document.getElementById("prod-img-card").src = src;
		});
		$( "#prod-card2" ).hover(function() {
			var src = document.getElementById("prod-card2").src;
			document.getElementById("prod-img-card").src = src;
		});

	

	
	
	
	
		function getFramedImg (prod_id, m_id, m_color, mount_size) {
			//var currwidth = parseFloat($("#size-slider").slider("value"));
			var currwidth = $("#i_width").val();
			
			var mnt_color = '';
			var mnt_size = '0'
			if (get_print_medium_id() == 'PAPER') {
				mnt_color = get_mount_color();
				mnt_size = get_mount_size()
			} else {
				mnt_color = '';
				mnt_size = '0'			
			}

			var str_canvas = 'NO';
			if (get_stretch_id() == '1') {
				str_canvas = 'YES';			
			}
			// Get the framed image
			$.ajax({
					url: "{% url 'get_framed_image' %}", 
					data: {'prod_id':prod_id, 'moulding_id': get_moulding_id(),
							'mount_color':mnt_color, 'mount_size':mnt_size, 'image_width':currwidth,
							'stretched_canvas': str_canvas
						}, 
					dataType: 'text', 
				success: function (data) {
					document.getElementById("prod-img-card").src = "data:image/png;base64," + data;
					document.getElementById("prod-img-card-thumb").src = "data:image/png;base64," + data;
					get_cards();
					document.body.scrollTop = 0; // For Safari
					document.documentElement.scrollTop = 0;
					
					
					getblob(moulding_id, mnt_color, mnt_size, currwidth, str_canvas);
					
					},
				error: function(xhr){
					alert("An error occured: " + xhr.status + " " + xhr.statusText); 
				}
			});
		}
	
	
	
	
		function set_size_slider(i_width, calc_cost=true, framing_typ='') {
			$("#i_width").val(i_width);
			set_image_width(parseFloat(i_width));

			var i_height = Math.round( i_width / ratio );
			$("#i_height").val(i_height);
			set_image_height(i_height);

			var minwidth = 8;
			var maxwidth = 48;
			var maxheigth = 48;
			var maxW_printer = 46;  
			var maxH_printer = Math.round( 46 * ratio );

			// Assing max size equal to printer max
			if (ratio <= 1) {
				maxW_printer = 48;
				maxH_printer = Math.round( maxW_printer / ratio );
			} else {
				maxH_printer = 48;
				maxW_printer = Math.round( maxH_printer * ratio );
			}
			maxwidth = maxW_printer;
			maxheight = maxH_printer;

						
			// Compare with prod max size and assign 
			var maxW_prod = parseFloat("{{product.max_width}}");
			var maxH_prod = Math.round( maxW_prod / ratio );		
			if (maxW_prod > maxW_printer && maxH_prod > maxH_printer) {
				if (ratio <= 1) {
					maxwidth = maxW_printer;
					maxheigth = Math.round( maxwidth / ratio );
				} else {
					maxheight = maxH_printer;
					maxwidth = Math.round( maxheight * ratio );
				}
			} else {
				if (maxW_prod < maxW_printer && maxH_prod < maxH_printer) {
					if (ratio <= 1) {
						maxwidth = maxW_prod;
						maxheigth = Math.round( maxwidth / ratio );
					} else {
						maxheight = maxH_prod;
						maxwidth = Math.round( maxheight * ratio );
					}				
				}
			}

			// Assign max size if it's paper with mount
			var mnt_size = get_mount_size();
			var mnt_id = get_mount_id();
			if (get_print_medium_id() == 'PAPER' && get_mount_id() != '' && get_mount_id() != '0' && mnt_size > 0){
				if ( ratio <= 1 ){
					max_height_with_mount = 40 -  mnt_size*2;
					max_width_with_mount = roundNum( max_height_with_mount * ratio);				
					if (max_height_with_mount > 60-mnt_size*2){
						max_height_with_mount = 60-mnt_size*2;
						max_width_with_mount = roundNum( max_height_with_mount * ratio);	
					}
				} else {
					max_width_with_mount = 40 -  mnt_size*2;
					max_height_with_mount = roundNum( max_width_with_mount / ratio);
					if (max_width_with_mount > 60-mnt_size*2){
						max_width_with_mount = 60-mnt_size*2;
						max_height_with_mount = roundNum( max_width_with_mount / ratio);	
					}
				}
				
				if (i_width > max_width_with_mount){
					if ( maxwidth > max_width_with_mount) {
						$("#i_width").val(max_width_with_mount);
						maxwidth = max_width_with_mount;
						i_width = max_width_with_mount;
						$("#i_height").val(max_height_with_mount);
						maxheight = max_height_with_mount;
					}
				}
			}

			
			{% if product.artist == "Huynh, Duy" %}
				if (ratio > 1){
					var hgt = 16;
					var wdth = Math.round(16 * {{product.aspect_ratio}});
					minwidth = wdth;
				} else {
					minwidth = 16;
				}
			{% endif %}		
			
			/*if ( $( "size-slider" ).slider( "instance" ) != null ) { 
				if (i_width == $( "#size-slider" ).slider( "value" ) ){
					return;
				}
			}*/

			if (i_width > maxwidth) {
				if (get_print_medium_id() == 'PAPER' && get_mount_id() != '' && get_mount_id() != '0' && mnt_size > 0){
					$("#mnt-size-msg").html("With " + mnt_size.toString() + " inch mount, the max print size can be upto " + maxwidth.toString() + " X " +  maxheight.toString() + " inch.");
					$("#mnt-size-msg").show();
					i_width = maxwidth;
					set_image_width(maxwidth);
					set_image_height(maxheight);

					$("#i_width").val(maxwidth);
					var w_cm  = parseFloat( maxwidth * 2.54);
					w_cm = +w_cm.toFixed(2);
					$("#a_width_cm").html( w_cm.toString() + " cm" );
					
					$("#i_height").val(maxheight);
					var h_cm  = parseFloat( maxheight * 2.54);
					h_cm = +h_cm.toFixed(2);
					$("#a_height_cm").html( h_cm.toString() + " cm" );
					
					print_size_display(maxwidth, maxheight);
				} else {
					$("#mnt-size-msg").html("The max print size can be upto " + maxwidth.toString() + " X " +  maxheight.toString() + " inch.");
					$("#mnt-size-msg").show();
				}
			} else {
				$("#mnt-size-msg").html("");
				$("#mnt-size-msg").hide();					
			}


			/*					
			$("#size-slider").slider({
				value:i_width,
				min:minwidth,
				max:maxwidth,
				step:1,
				change:function(event, ui){
					var currwidth = ui.value;
					var currheight = roundNum(currwidth / ratio);
					set_image_width(currwidth);
					set_image_height(currheight);

					$("#i_width").val(currwidth);
					var w_cm  = parseFloat( currwidth * 2.54);
					w_cm = +w_cm.toFixed(2);
					$("#a_width_cm").html( w_cm.toString() + " cm" );					

					$("#i_height").val(currheight);
					var h_cm  = parseFloat( currheight * 2.54);
					h_cm = +h_cm.toFixed(2);
					$("#a_height_cm").html( h_cm.toString() + " cm" );
				
					print_size_display(currwidth, currheight, get_framing_type());
					if (calc_cost) {
						calc_total_price();
					}
					if ( fetch_img_on_slide == false ) {
						fetch_img_on_slide = true;
					} else {
 						//getFramedImg (product_id, moulding_id, mount_color, mount_size);
					}
				}
			});

			if (calc_cost) {
				calc_total_price();
			}*/
		}
	
		$("#i_width").change(function() {

			var currwidth = $( this ).val();
			var currheight = roundNum(currwidth / ratio);
			var w_cm  = parseFloat( currwidth * 2.54);
			w_cm = +w_cm.toFixed(2);
			$("#a_width_cm").html( w_cm.toString() + " cm" );					

			$("#i_height").val(currheight);
			var h_cm  = parseFloat( currheight * 2.54);
			h_cm = +h_cm.toFixed(2);
			$("#a_height_cm").html( h_cm.toString() + " cm" );
		
			calc_total_price();
			print_size_display(currwidth, currheight, get_framing_type());
			if ( fetch_img_on_slide == false ) {
				fetch_img_on_slide = true;
			} else {
				//getFramedImg (product_id, moulding_id, mount_color, mount_size);
			}
		});

	
	

	
	function calc_total_price(){
		//var ratio = parseFloat("{{product.aspect_ratio}}"); 
		//var currwidth = parseFloat($("#size-slider").slider("value"));
		var currwidth = parseFloat($("#i_width").val());
		//var currheight = Math.round(currwidth / ratio);
		var currheight = roundNum(currwidth / ratio);
		var sqin = currwidth * currheight;
		var rnin = (currwidth + currheight) * 2;
		var image_price = 0;
		var total_price = 0;
		var acr_id = get_acrylic_id();
		var brd_id = get_board_id();
		var mnt_id = get_mount_id();
		
		//Get Print Medium
		//var print_medium = $('#print-medium-select').val();
		var print_med = get_print_medium_id();
		
		// Set the pricing compoenents appropriately:
		if (print_med == 'PAPER') {
			if (moulding_id == '0' || moulding_id == '' || moulding_id == null){
				acr_id = '0';
				brd_id = '0';
				mnt_id = '0';
			}
			set_stretch_id('0');
		} else {				
			acr_id = '0';
			brd_id = '0';
			mnt_id = '0';
		}
		
		var str_id = stretch_id;
		
		if	(moulding_id != '' && moulding_id != '0' && print_med == 'CANVAS'){
			str_id = 1;		
		}
		
		if (moulding_id == ''){
			moulding_id = '0';
		}


		// Form the pricing components
		json = '{ ' + 
				'"IMAGE": {"WIDTH":' + currwidth + ', "HEIGHT":' + currheight + '}, ' + 
				'"PRINT_MEDIUM": {"ID" :"' + print_med + '", "SIZE":' + sqin + '}, ' +
				'"ACRYLIC": {"ID" :' + acr_id + ', "SIZE":' + sqin + '}, ' +
				'"MOULDING": {"ID" :' + moulding_id + ', "SIZE":' + rnin + '}, ' +
				'"MOUNT": {"ID" :' + mnt_id + ', "SIZE":' + mount_size + '}, ' +
				'"BOARD": {"ID" :' + brd_id + ', "SIZE":' + sqin + '}, ' +
				'"STRETCH": {"ID" :' + str_id + ', "SIZE":' + rnin + '}, ' +
				'"PRODUCT": {"ID" :' + product_id + ', "SIZE":' + rnin + '}, ' +
				'"PRODUCT_TYPE": {"ID" :"STOCK-IMAGE", "SIZE":' + rnin + '} ' +
				'}';			
		
		
		// GET ITEM PRICE
		$.ajax({
				url: "{% url 'get_item_price' %}", 
				data: json, 
				dataType: 'text', 
				type: 'POST',
				success: function (data) {
					data = JSON.parse(data);
					msg = data.msg.toUpperCase();
					if (data.msg.toUpperCase() == 'SUCCESS') { 
						if (data.disc_applied) {
							$("#no-disc").hide();
							$("#promo-display").show("slow");
							$("#item_unit_price").html(data.item_unit_price);
							$("#item_total_price").html(data.item_price);
							if ( parseInt(data.cash_disc) > 0 ) {
								$("#disc").html("(" + data.cash_disc + " off)");
							} else if( parseInt(data.percent_disc) > 0 ) {
								$("#disc").html("(" + data.percent_disc + "% off)");
							}
							
							$("#item_unit_price_nv").html(data.item_unit_price);
							$("#promotion_id_nv").html(data.promotion_id);
							$("#disc_amt_nv").html(data.disc_amt);
							$("#item_total_price_nv").html(data.item_price);
							$("#prod-price-cart").html(data.item_price);
							
						} else {
							$("#promo-display").hide();
							$("#no-disc").show();
							$("#prod-price").html(data.item_price);
							$("#prod-price-cart").html(data.item_price);

							$("#item_unit_price_nv").html(data.item_unit_price);
							$("#item_total_price_nv").html(data.item_price);
							$("#promotion_id_nv").html('');
							$("#disc_amt_nv").html('');
						}
					} else {
						alert(msg);
							$("#promo-display").hide();
							$("#no-disc").show();
							
							$("#item_unit_price_nv").html(data.item_unit_price);
							$("#item_total_price_nv").html(data.item_price);
							$("#promotion_id_nv").html('');
							$("#disc_amt_nv").html('');
					}								
				},
				error: function(xhr){
					//alert("An error occured: " + xhr.status + " " + xhr.statusText); 
				}
		});		
				
	}		
	
	
	
	
		function addProdToCart(prod_id, qty) {
			var cart_qty;
			var total_price = $("#item_total_price_nv").html();	
			if (total_price == '0'){
				alert("Sorry, this product is not available.");
				return;
			}			
			var discount = $("#disc").html();
			var promotion_id = $("#promotion_id_nv").html();
			var disc_amt = $("#disc_amt_nv").html();
			var item_unit_price = $("#item_unit_price_nv").html();

			var m_size = parseInt($('#mount-size').val());
			if(typeof m_size == "undefined"){			
				alert("Sorry, mount width can be between 1 and 5 inch.");
				return;
			}
			if ( m_size > 5 ){
				alert("Sorry, mount width can be between 1 and 5 inch.");
				return;
			}
			
			//var ratio = parseFloat("{{product.aspect_ratio}}"); 
			//var currwidth = parseFloat($("#size-slider").slider("value"));
			var currwidth = parseFloat($("#i_width").val());
			//var currheight = Math.round(currwidth / ratio);
			var currheight = roundNum(currwidth / ratio);
			var sqin = currwidth * currheight;
			
			//print_medium_id = $('#print-medium-select').val();
			print_medium_id = get_print_medium_id();
			print_medium_size = sqin;
			moulding_size = (currwidth + currheight) * 2;
			//mount_size = (currwidth + currheight) * 2;  // Taken from the mout_size set earlier (not sqin)
			acrylic_size = currwidth * currheight;
			board_size = currwidth * currheight;
			stretch_size = (currwidth + currheight) * 2;
			
			var acr_id = '';
			var brd_id = '';
			var str_id = '';
			var mnt_id = '';
			if (print_medium_id == 'CANVAS') {
				var str_id = get_stretch_id();
				mnt_id = '0'
			} else {
				if (moulding_id != '' && moulding_id != '0') {
					var acr_id = get_acrylic_id();
					var brd_id = get_board_id();
					mnt_id = get_mount_id();
				} else {
					var acr_id = '';
					var brd_id = '';
					mnt_id = '';
				}
				var str_id = '';
			}
			
			//
			var cart_item_flag = 'FALSE';
			{% if cart_item %}
				cart_item_flag = 'TRUE';
			{% endif %}
			
			// Update the cart
			$.ajax({
				url: "{% url 'add_to_cart' %}", 
				data: {'prod_id':prod_id, 'qty':qty, 'moulding_id': moulding_id,
						'width':currwidth, 'height':currheight,
						'moulding_size' : moulding_size,
						'print_medium_id':print_medium_id, 'print_medium_size':print_medium_size, 
						'mount_id':mnt_id, 'mount_size':mount_size,
						'mount_w_left' : mount_w_left, 'mount_w_right':mount_w_right, 
						'mount_w_top':mount_w_top, 'mount_w_bottom' : mount_w_bottom, 
						'acrylic_id':acr_id, 'acrylic_size':acrylic_size,
						'board_id':brd_id, 'board_size':board_size, 'stretch_id':str_id,
						'stretch_size':stretch_size, 
						'total_price':total_price, 'image_width':currwidth, 'image_height':currheight,
						'discount':discount, 'promotion_id':promotion_id, 'disc_amt':disc_amt,
						'item_unit_price':item_unit_price, 'prod_type':'STOCK-IMAGE',
						'cart_item_flag':cart_item_flag}, 
				dataType: 'text', 
					type: 'POST',
				success: function (data) {
					data = JSON.parse(data);
					if (data.msg.toUpperCase() != 'SUCCESS'){
							alert(data.msg);
					} else {					
							
						cart_qty = data.cart_qty;
						//Update items in cart
						//$("#itemsincart").html(cart_qty); 
						updateCartItemsNum(cart_qty);
						$('#cart-msg-modal').modal('show');					

						/*
						{% if env == 'PROD' %}
						gtag('event','add_to_cart', {
						  'value': total_price,
						  'items':[{
						  'id':prod_id,
						  'location_id': '',
						  'google_business_vertical': 'custom',
						  }]
						  });
						{% endif %}
						*/
						wigzo ("track", "addtocart", "https://artevenue.com/art-print/" + prod_id.toString() + "/");
					}
				},
				error: function(xhr){
					alert("An error occured: " + xhr.status + " " + xhr.statusText); 
				}
			});			

		}
			
		// ---- Add Product to Cart ----//
		function addProdToWishlist(prod_id, qty) {
			var cart_qty;
			var total_price = $("#item_total_price_nv").html();
			if (total_price == '0'){
				alert("Sorry, this product is not available.");
				return;
			}
			var discount = $("#disc").html();
			var promotion_id = $("#promotion_id_nv").html();
			var disc_amt = $("#disc_amt_nv").html();
			var item_unit_price = $("#item_unit_price_nv").html();
	
			var img = document.getElementById('prod-img');
			var width = img.naturalWidth;
			var height = img.naturalHeight;
			var img = document.getElementById('prod-img');
			//var currwidth = parseFloat($("#size-slider").slider("value"));
			var currwidth = parseFloat($("#i_width").val());
			//var currheight = Math.round(currwidth / ratio);
			var currheight = roundNum(currwidth / ratio);
			var sqin = currwidth * currheight;
			
			//print_medium_id = $('#print-medium-select').val();
			print_medium_size = sqin;
			moulding_size = (currwidth + currheight) * 2;
			acrylic_size = currwidth * currheight;
			board_size = currwidth * currheight;
			stretch_size = (currwidth + currheight) * 2;
			
			if (print_medium_id == 'CANVAS') {
				var acr_id = '';
				var brd_id = '';
				var str_id = get_stretch_id();
			} else {
				var acr_id = get_acrylic_id();
				var brd_id = get_board_id();
				var str_id = '';
			}

			//
			var wishlist_item_flag = 'FALSE';
			{% if wishlist_item %}
				wishlist_item_flag = 'TRUE';
			{% endif %}
			
			// Update the cart
			$.ajax({
				url: "{% url 'add_to_wishlist' %}", 
				data: { 'prod_id':prod_id,'qty':qty, 
						'width':currwidth, 'height':currheight, 'moulding_id': moulding_id,
						'moulding_size' : moulding_size,
						'print_medium_id':print_medium_id, 'print_medium_size':print_medium_size, 
						'mount_id':mount_id, 'mount_size':mount_size,
						'mount_w_left' : mount_w_left, 'mount_w_right':mount_w_right, 
						'mount_w_top':mount_w_top, 'mount_w_bottom' : mount_w_bottom, 
						'acrylic_id':acr_id, 'acrylic_size':acrylic_size,
						'board_id':brd_id, 'board_size':board_size, 'stretch_id':str_id,
						'stretch_size':stretch_size, 
						'total_price':total_price, 'image_width':currwidth, 'image_height':currheight,
						'discount':discount, 'promotion_id':promotion_id, 'disc_amt':disc_amt,
						'item_unit_price':item_unit_price,  'prod_type':'STOCK-IMAGE',
						'wishlist_item_flag':wishlist_item_flag}, 
				dataType: 'text', 
					type: 'POST',
				success: function (data) {
					data = JSON.parse(data);
					cart_qty = data.cart_qty;
					//Update items in cart
					$('#msg-wishlist-modal').modal('show');
				},
				error: function(xhr){
					alert("An error occured: " + xhr.status + " " + xhr.statusText); 
				}
			});

		}				
	
	
			
	
		function set_ready_product(print_med, framing_type, prod_width, prod_height, unframed_width, unframed_height, mld_id, mnt_id, mnt_size, mnt_color, acr_id, brd_id, str_id, fetch_img=true){

			var prod_id = get_product_id();
			set_image_width(unframed_width);
			set_image_height(unframed_height);
			set_size_slider(unframed_width, false);
			set_mount_id(mnt_id);
			set_mount_size(mnt_size);
			set_mount_color(mnt_color);
			set_board_id(brd_id);
			set_acrylic_id(acr_id);
			set_moulding_id(mld_id);
			set_stretch_id(str_id);

			switch(framing_type) {
				case 'PAPER_ROLLED':
					buy_without_frame_change(true, false, false);
					break;
				case 'PAPER_FRAMED_WITH_MOUNT':
					moulding_change(mld_id, false,false)
					break;
				case 'PAPER_FRAMED_WITHOUT_MOUNT':
					moulding_change(mld_id, false, false)
					break;
				case 'CANVAS_ROLLED':
					buy_without_frame_change(true, false, false);
					break;
				case 'CANVAS_FRAMED':
					moulding_change(mld_id, false, false)
					break;
				case 'CANVAS_STRETCHED':
					set_mount_id('');
					moulding_change('', false, false)
					break;
			}

			calc_total_price();
			print_size_display(unframed_width, unframed_height, framing_type);

			if  ( fetch_img == false ){
				fetch_img_on_slide = true;
			}
						
		}
	
	
	
	function get_cards(){
		// Get the card
		var prod_id = get_product_id();
		//var currwidth = parseFloat($("#size-slider").slider("value"));
		var currwidth = parseFloat($("#i_width").val());
		var m_id = get_moulding_id();
		var mnt_color = '';
		var mnt_size = '0'
		if (get_print_medium_id() == 'PAPER') {
			mnt_color = get_mount_color();
			mnt_size = get_mount_size()
		} else {
			mnt_color = '';
			mnt_size = '0';			
		}
		var str_canvas = 'NO';
		if (get_stretch_id() == '1') {
			str_canvas = 'YES';			
		}


		if ((m_id != '' && m_id != '0') || (str_canvas == 'YES')) {
			// Get the framed image
			$.ajax({
					url: "{% url 'get_framed_image' %}", 
					data: {'prod_id':prod_id, 'moulding_id': m_id,
							'mount_color':mnt_color, 'mount_size':mnt_size, 'image_width':currwidth,
							'stretched_canvas': str_canvas, 'imgtilt': 'NO'
						}, 
					dataType: 'text', 
				success: function (data) {
					document.getElementById("prod-card1").src = "data:image/png;base64," + data;				
					$("#prod-card1").css('display', 'block');
					
					// Assign the blob and enable AR
					getblob(moulding_id, mnt_color, mnt_size, currwidth, str_canvas);
					
					},
				error: function(xhr){
					alert("An error occured: " + xhr.status + " " + xhr.statusText); 
				}
			});
		} else {
			$("#prod-card1").css('display', 'none');
		}
		

		$.ajax({
				url: "{% url 'get_catalog_card' %}", 
				data: {'card_no': '2', 'prod_id':prod_id, 'moulding_id': m_id,
						'mount_color':mnt_color, 'mount_size':mnt_size, 
						'image_width':currwidth, 'prod_type':'STOCK-IMAGE'
					}, 
				dataType: 'text', 
			success: function (data) {
				document.getElementById("prod-card2").src = "data:image/png;base64," + data;				
				},
			error: function(xhr){
				alert("An error occured: " + xhr.status + " " + xhr.statusText); 
			}
		});
	}
	
	
	
	$( "#prod-img-card-thumb" ).click(function() {
		var src = document.getElementById("prod-img-card-thumb").src;
		document.getElementById("prod-img-card").src = src;
	});
	$( "#prod-card1" ).click(function() {
		var src = document.getElementById("prod-card1").src;
		document.getElementById("prod-img-card").src = src;
	});
	$( "#prod-card2" ).click(function() {
		var src = document.getElementById("prod-card2").src;
		document.getElementById("prod-img-card").src = src;
	});
		
	
		
	
	
		function donwloadImage() {		
			var img_src = document.getElementById("prod-img").src;
			var fileName = String(get_product_id()) + "_img.jpg";			
			var link = document.createElement("a");
			document.body.appendChild(link); // for Firefox
			link.setAttribute("href", img_src);
			link.setAttribute("download", fileName);
			link.click();
		}
	
	
		function roundNum(value) {
			var x = Math.floor(value);
			if ((value - x) <= 0.50) {
				return x;
			} else {
				return Math.ceil(value);
			}
		}
	

	
	window.onscroll = function() {scrollFunction()};
	var scrbutton = document.getElementById("scrollBtn");

	function scrollFunction() {
	  if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
		scrbutton.style.display = "block";
	  } else {
		scrbutton.style.display = "none";
	  }
	}

	// When the user clicks on the button, scroll to the top of the document
	function topFunction() {
	  document.body.scrollTop = 0;
	  document.documentElement.scrollTop = 0;
	}
		
	
	
	function set_prod_diagram_and_frame(){
		set_frame_img(get_moulding_id());
		if ( get_print_medium_id() == 'PAPER' && (get_mount_id() != '' && get_mount_id() != '0' && mount_size != 0) && (get_moulding_id() != '' && get_moulding_id() != '0') ){
			$("#prod-diagram").show();
			$("#components").prop("src", "{% static 'img/prod_desc/paper_frame_mount-min.png' %}" );
			$("#components").attr("data-src", "{% static 'img/prod_desc/paper_frame_mount-min.png' %}" );
			$("#no_frame_msg").hide();
			$("#frame_msg").show();
			$("#d-hanging").show();
			$("#d-packing").show();
		} else if ( get_print_medium_id() == 'PAPER' && (get_mount_id() == '' || get_mount_id() == '0') && (get_moulding_id() != '' && get_moulding_id() != '0') ){
			$("#prod-diagram").show();
			$("#components").prop("src", "{% static 'img/prod_desc/paper_frame_no_mount-min.png' %}" );
			$("#components").attr("data-src", "{% static 'img/prod_desc/paper_frame_no_mount-min.png' %}" );
			$("#no_frame_msg").hide();
			$("#frame_msg").show();
			$("#d-hanging").show();
			$("#d-packing").show();
		} else if ( get_print_medium_id() == 'CANVAS' && (get_moulding_id() != '' && get_moulding_id() != '0') ){
			$("#prod-diagram").show();
			$("#components").prop("src", "{% static 'img/prod_desc/canvas_frame-min.png' %}" );							
			$("#components").attr("data-src", "{% static 'img/prod_desc/canvas_frame-min.png' %}" );							
			$("#no_frame_msg").hide();
			$("#frame_msg").show();
			$("#d-hanging").show();
			$("#d-packing").show();
		} else if ( get_print_medium_id() == 'PAPER' && (get_mount_id() == '' || get_mount_id() == '0') && (get_moulding_id() == '' || get_moulding_id() == '0') ){
			$("#prod-diagram").show();
			$("#components").prop("src", "{% static 'img/prod_desc/paper_print-min.png' %}" );
			$("#components").attr("data-src", "{% static 'img/prod_desc/paper_print-min.png' %}" );
			$("#no_frame_msg").show();
			$("#frame_msg").hide();
			$("#d-hanging").hide();
			$("#d-packing").hide();
		} else if ( get_print_medium_id() == 'CANVAS'&& (get_moulding_id() == '' || get_moulding_id() == '0')  && get_stretch_id() != '1'){
			$("#prod-diagram").show();
			$("#components").prop("src", "{% static 'img/prod_desc/canvas_print-min.png' %}" );
			$("#components").attr("data-src", "{% static 'img/prod_desc/canvas_print-min.png' %}" );
			$("#no_frame_msg").show();
			$("#frame_msg").hide();
			$("#d-hanging").hide();
			$("#d-packing").hide();
		} else if ( get_print_medium_id() == 'CANVAS' && (get_moulding_id() == '' || get_moulding_id() == '0') && get_stretch_id() == '1'){
			$("#prod-diagram").hide();
			$("#frame_msg").hide();
			$("#d-hanging").show();
			$("#d-packing").show();
		} else {
			$("#prod-diagram").hide();
			$("#no_frame_msg").hide();
			$("#frame_msg").hide();
			$("#d-hanging").hide();
			$("#d-packing").hide();
		}
	}
	
	
	
		function set_max_size_with_mount(calc_cost=true){
		
			var mnt_size = get_mount_size();
			var mnt_id = get_mount_id();
			var wdt = get_image_width();
			set_size_slider(wdt, calc_cost);
			/*
			if (get_print_medium_id() == 'PAPER' && get_mount_id() != '' && get_mount_id() != '0' && mnt_size > 0){
				var currwidth = get_image_width();
				var currheight = get_image_height();
				var max_width = 60 - mnt_size*2;
				var max_height = 60 - mnt_size*2;
				
				if (ratio >= 1){
					if (currwidth > max_width) {
						set_size_slider(max_width, calc_cost);
						var h = Math.round(max_width / ratio);
						$("#mnt-size-msg").html("With " + mnt_size.toString() + " inch mount, the max print size can be upto " + max_width.toString() + " X " +  h.toString() + " inch.");
						$("#mnt-size-msg").show();
					} else {
						$("#mnt-size-msg").hide();
					}
				} else {
					if (currheight > max_height) {
						var w = Math.round(max_height * ratio);
						set_size_slider(w, calc_cost);
						$("#mnt-size-msg").html("With " + mnt_size.toString() + " inch mount, the max print size can be upto " + w.toString() + " X " +  max_height.toString() + " inch.");
						$("#mnt-size-msg").show();
					} else {
						$("#mnt-size-msg").hide();
					}
				}
			} else {
				var wdt = get_image_width();
				$("#mnt-size-msg").hide();
				set_size_slider(wdt, calc_cost);
			}*/
		}	
	

	
		async function getblob(moulding_id, mnt_color, mnt_size, currwidth, str_canvas){
			if (ratio >= 1){
				var wdt = 1000;			
				var hgt = Math.round(1000 / ratio);
			} else {
				var hgt = 1000;			
				var wdt = Math.round(1000 * ratio);
			}
			var base64string = document.getElementById("prod-card1").src;
			var mount_col = mnt_color.replace('#','');
			document.getElementById("av-helloar-button").setAttribute('data-image-blob', base64string  );
			document.getElementById("av-helloar-button").setAttribute("data-valid", "true");
			document.getElementById("av-helloar-button").setAttribute("data-image-width", wdt);
			document.getElementById("av-helloar-button").setAttribute("data-image-height", hgt);
			document.getElementById("av-helloar-button").setAttribute('data-unique-id', '{{product.product_id}}' + '-' + moulding_id + '-' + mount_col + '-' + mnt_size + '-' + currwidth + '-' + str_canvas );
			HelloManager.insertHelloButton();
		}	

	
	
	
		var flip_box_visibility = "FRONT";

		$("#i_customize").click(function(){
			$('.flip-box-inner').css('transform', 'rotateY(180deg)'); 
			var hgt = $("#customize-sec").height() + 15;
			if (get_print_medium_id() == 'CANVAS') {
				$('.flip-box').css('height',hgt);
			} else {
				$('.flip-box').css('height',hgt);
			}
			flip_box_visibility = "BACK";
		});
		$("#i_standard").click(function(){
			var hgt = $("#standard-sec").height() + 15;
			$('.flip-box-inner').css('transform', 'rotateY(0deg)'); 
			$('.flip-box').css('height',hgt);
			flip_box_visibility = "FRONT";
		});
	

	
		function framing_type_chaged(prt_med, typ, set_default_size=true, fetch_img=true){
			set_framing_type(typ);
			if (prt_med == 'PAPER') {
				if (typ == 'PAPER_FRAMED_WITH_MOUNT') {
					$('#dropdownMenu_type_paper').prop('value', 'PAPER_FRAMED_WITH_MOUNT'); 
					$('#dropdownMenu_type_paper').text("FRAMED");
					$('#frames-slider-paper *').prop('disabled',false);

					$("#sizes_paper_unframed").hide();
					$("#sizes_paper_framed_with_mount").show();
					$("#sizes_paper_framed_without_mount").hide();
					$("#sizes_canvas_rolled").hide();
					$("#sizes_canvas_framed").hide();
					$("#sizes_canvas_stretched").hide();

					$("#mount-show").show();

					if (set_default_size) {
						{% for key, value in ready_prod_data_paper.items %}
						{% if value.PAPER_DEFAULT_WIDTH_FRAMED_WITH_MOUNT %}
						wd = {{ value.PAPER_WIDTH_UNFRAMED|floatformat }};
						ht = {{ value.PAPER_HEIGHT_UNFRAMED|floatformat }};
						set_ready_product('PAPER', 'PAPER_FRAMED_WITH_MOUNT', {{value.PAPER_WIDTH_FRAMED_WITH_MOUNT}}, {{value.PAPER_HEIGHT_FRAMED_WITH_MOUNT}}, wd, ht, {{value.MOULDING_ID}}, {{value.MOUNT_ID}}, {{value.MOUNT_SIZE}}, '{{value.MOUNT_COLOR}}', {{value.ACRYLIC_ID}},  {{value.BOARD_ID}}, {{value.STRETCH_ID}}, true);
						print_size_display(wd, ht,'PAPER_FRAMED_WITH_MOUNT');
						{% endif %}
						{% endfor %}
					} else {
						// Set mount
						var mnt_size = $("#mount-size").val();
						if (mnt_size < 1) {
							var mnt_size = 1;
							if ( get_image_width() > 26 ) {
								mnt_size = 2;
							}
						}
						set_mount_id('3');
						set_mount_size(mnt_size);
						set_mount_color( '#fffff0' );

						var m_id = get_moulding_id();
						if (m_id == '0' || m_id == ''){
							moulding_change('18', false, false);
						} else {
							moulding_change(m_id, false, false);
						}
						calc_total_price();
						print_size_display(image_width, image_height ,'PAPER_FRAMED_WITH_MOUNT');
					}
					$("#mount-size").val(mount_size);
				}
				if (typ == 'PAPER_FRAMED_WITHOUT_MOUNT') {
					$('#dropdownMenu_type_paper').prop('value', 'PAPER_FRAMED_WITHOUT_MOUNT'); 
					$('#dropdownMenu_type_paper').text("FRAMED (WITHOUT MOUNT)");
					$('#frames-slider-paper *').prop('disabled',false);

					$("#sizes_paper_unframed").hide();
					$("#sizes_paper_framed_with_mount").hide();
					$("#sizes_paper_framed_without_mount").show();
					$("#sizes_canvas_rolled").hide();
					$("#sizes_canvas_framed").hide();
					$("#sizes_canvas_stretched").hide();					

					$("#mount-show").hide();
					$("#mount-size").val(0);

					if (set_default_size) {
						{% for key, value in ready_prod_data_paper.items %}
						{% if value.PAPER_DEFAULT_WIDTH_FRAMED_WITHOUT_MOUNT %}
						wd = {{ value.PAPER_WIDTH_UNFRAMED|floatformat }};
						ht = {{ value.PAPER_HEIGHT_UNFRAMED|floatformat }};
						set_ready_product('PAPER', 'PAPER_FRAMED_WITHOUT_MOUNT', {{value.PAPER_WIDTH_FRAMED_WITHOUT_MOUNT}}, {{value.PAPER_HEIGHT_FRAMED_WITHOUT_MOUNT}}, wd, ht,  {{value.MOULDING_ID}}, 0, 0, '', {{value.ACRYLIC_ID}},  {{value.BOARD_ID}}, 0, true);
						print_size_display(wd, ht ,'PAPER_FRAMED_WITHOUT_MOUNT');
						{% endif %}
						{% endfor %}
					} else {
						// Remove Mount
						set_mount_id('0');
						set_mount_size(0);
						set_mount_color( '' )
						$("#mount-size").val(0);

						var m_id = get_moulding_id();
						if (m_id == '0' || m_id == ''){
							moulding_change('18', false, false);
						} else {
							moulding_change(m_id, false, false);
						}
						calc_total_price();
						print_size_display(image_width, image_height, 'PAPER_FRAMED_WITHOUT_MOUNT');
					}
					
				}
				if (typ == 'PAPER_ROLLED') {
					$('#dropdownMenu_type_paper').prop('value', 'PAPER_ROLLED');
					$('#dropdownMenu_type_paper').text("ROLLED PAPER PRINT");
					$('#dropdownMenu_paper').html('No Frame');
					$('#frames-slider-paper *').prop('disabled',true);

					$("#sizes_paper_unframed").show();
					$("#sizes_paper_framed_with_mount").hide();
					$("#sizes_paper_framed_without_mount").hide();
					$("#sizes_canvas_rolled").hide();
					$("#sizes_canvas_framed").hide();
					$("#sizes_canvas_stretched").hide();

					$("#mount-show").hide();
					$("#mount-size").val(0);

					if (set_default_size) {
						{% for key, value in ready_prod_data_paper.items %}
						{% if value.PAPER_DEFAULT_WIDTH_ROLLED %}
						wd = {{ value.PAPER_WIDTH_UNFRAMED|floatformat }};
						ht = {{ value.PAPER_HEIGHT_UNFRAMED|floatformat }};
						set_ready_product('PAPER', 'PAPER_ROLLED', {{value.PAPER_WIDTH_ROLLED}}, {{value.PAPER_HEIGHT_ROLLED}}, wd, ht, 0, 0, 0, '', 0,  0, 0, true);
						print_size_display(wd, ht,'PAPER_ROLLED');
						{% endif %}
						{% endfor %}
					} else {
						// Remove frame, mount
						set_mount_size('0');
						set_mount_color( '' );
						set_moulding_id( '' );
						buy_without_frame_change(true, false, false )
						calc_total_price();
						print_size_display(image_width, image_height, 'PAPER_ROLLED');
					}
				}
	
			}
			if (prt_med == 'CANVAS') {
				if (typ == 'CANVAS_FRAMED') {
					$('#dropdownMenu_type_canvas').prop('value', 'CANVAS_FRAMED'); 
					$('#dropdownMenu_type_canvas').text("FRAMED");
					$('#frames-slider-canvas *').prop('disabled', false);

					$("#sizes_paper_unframed").hide();
					$("#sizes_paper_framed_with_mount").hide();
					$("#sizes_paper_framed_without_mount").hide();
					$("#sizes_canvas_rolled").hide();
					$("#sizes_canvas_framed").show();
					$("#sizes_canvas_stretched").hide();					
					if (set_default_size) {
						{% for key, value in ready_prod_data_canvas.items %}
						{% if value.CANVAS_FRAMED_DEFAULT_WIDTH %}
						wd = {{ value.CANVAS_WIDTH_UNFRAMED|floatformat }};
						ht = {{ value.CANVAS_HEIGHT_UNFRAMED|floatformat }};
						set_ready_product('CANVAS', 'CANVAS_FRAMED', {{value.CANVAS_FRAMED_WIDTH|floatformat}}, {{value.CANVAS_FRAMED_HEIGHT|floatformat}}, wd, ht, {{value.MOULDING_ID}}, 0, 0, '', 0,  0, {{value.STRETCH_ID}}, true);
						print_size_display(wd, ht, 'CANVAS_FRAMED');
						{% endif %}
						{% endfor %}
					} else {
						// Set default, or selected framed id
						var m_id = get_moulding_id();
						if (m_id == '0' || m_id == ''){
							moulding_change('26', fetch_img, calc_cost);;
						} else {
							moulding_change(m_id, fetch_img, calc_cost);
						}
						set_stretch_id( '1' );
						
						calc_total_price();
						print_size_display(image_width, image_height, 'CANVAS_FRAMED');
					}
				}
				if (typ == 'CANVAS_STRETCHED') {
					$('#dropdownMenu_type_canvas').prop('value', 'CANVAS_STRETCHED'); 
					$('#dropdownMenu_type_canvas').text("STRETCHED CANVAS");
					$('#dropdownMenu_canvas').html('Streched Canvas');
					$('#frames-slider-canvas *').prop('disabled',true);

					$("#sizes_paper_unframed").hide();
					$("#sizes_paper_framed_with_mount").hide();
					$("#sizes_paper_framed_without_mount").hide();
					$("#sizes_canvas_rolled").hide();
					$("#sizes_canvas_framed").hide();
					$("#sizes_canvas_stretched").show();					
					if (set_default_size) {
						{% for key, value in ready_prod_data_canvas.items %}
						{% if value.CANVAS_STRETCHED_DEFAULT_WIDTH %}
						wd = {{ value.CANVAS_WIDTH_UNFRAMED|floatformat }};
						ht = {{ value.CANVAS_HEIGHT_UNFRAMED|floatformat }};
						set_ready_product('CANVAS', 'CANVAS_STRETCHED', {{value.CANVAS_STRETCHED_WIDTH}}, {{value.CANVAS_STRETCHED_HEIGHT}}, wd, ht, 0, 0, 0, '', 0, 0, {{value.STRETCH_ID}}, true);
						print_size_display(wd, ht ,'CANVAS_STRETCHED');
						{% endif %}
						{% endfor %}
					} else {
						// Set default, or selected framed id
						var m_id = get_moulding_id();
						set_moulding_id( '' );
						set_stretch_id( '1' );
						stretch_changed(false,false)
						calc_total_price();
						print_size_display(image_width, image_height, 'CANVAS_STRETCHED');
					}
				}
				if (typ == 'CANVAS_ROLLED') {
					$('#dropdownMenu_type_canvas').prop('value', 'CANVAS_ROLLED');
					$('#dropdownMenu_type_canvas').text("ROLLED CANVAS PRINT");
					$('#dropdownMenu_canvas').html('No Frame');
					$('#frames-slider-canvas *').prop('disabled',true);

					$("#sizes_paper_unframed").hide();
					$("#sizes_paper_framed_with_mount").hide();
					$("#sizes_paper_framed_without_mount").hide();
					$("#sizes_canvas_rolled").show();
					$("#sizes_canvas_framed").hide();
					$("#sizes_canvas_stretched").hide();
					if (set_default_size) {
						{% for key, value in ready_prod_data_canvas.items %}
						{% if value.CANVAS_DEFAULT_WIDTH_ROLLED %}
						wd = {{ value.CANVAS_WIDTH_UNFRAMED|floatformat }};
						ht = {{ value.CANVAS_HEIGHT_UNFRAMED|floatformat }};
						set_ready_product('CANVAS', 'CANVAS_ROLLED', {{value.CANVAS_WIDTH_ROLLED}}, {{value.CANVAS_HEIGHT_ROLLED}}, wd, ht, 0, 0, 0, '', 0,  0, 0, true);						
						{% endif %}
						{% endfor %}
					} else {
						set_moulding_id( '' );
						set_stretch_id( '' );
						buy_without_frame_change(true, false, false )
						calc_total_price();
						print_size_display(image_width, image_height, 'CANVAS_ROLLED');
					}
				}

			}
			//calc_total_price(); // Already done on set_ready_product function
			if (fetch_img){
				getFramedImg (get_product_id(), get_moulding_id(), get_mount_color(), get_mount_size());
			}

			if ( flip_box_visibility == 'FRONT' ){
				var hgt = $("#standard-sec").height() + 15;
				$('.flip-box-inner').css('transform', 'rotateY(0deg)'); 
				$('.flip-box').css('height',hgt);
			}

			if ( flip_box_visibility == 'BACK' ){
				$('.flip-box-inner').css('transform', 'rotateY(180deg)'); 
				var hgt = $("#customize-sec").height() + 15;
				if (get_print_medium_id() == 'CANVAS') {
					$('.flip-box').css('height',hgt);
				} else {
					$('.flip-box').css('height',hgt);
				}
			}

		}
	
