/**
 * Created by Aggelos.
 */



    // Due to the API of jQuery.dataTables, each handler regarding a button on a row/cell of the matrix, needs to be initialized
    // right after the button was created. This means that the handlers will be declared inside the function that creates the table.
    // We are sorry for the 'dirty'-looking code, but dataTables doesnt support a proper API for a creation of buttons or elements
    // and handlers after the table has been initialized.
	var table = $('#GoalTable').DataTable( {
					"sDom": "<'row-fluid'<'span6'l><'span6'f>r>t<'row-fluid'<'span12'i><'span12 center'p>>",
					"sPaginationType": "bootstrap",
        			"autoWidth": false,
					"oLanguage": {
						"sLengthMenu": "_MENU_  Records per page"
					},
					"ajax": BASE_URL + 'goals/goalstojson/',
					"columns":  [
						{ "data": "goal" },
						{ "data": "date" },
						{ "data": "activity" },
						{ "data": "goal_status" },
						{ "data": "id" }
					],
					"columnDefs": [{
                    "targets":0,
                    "createdCell": function(td, cellData, rowData, row, col) {
                        	$(td).empty();
                        	// We will create a code that switches the content of the 1st column between "input" and "a" html elements
                        	var clickableGoal = document.createElement('a');
                        	clickableGoal.href = "#"; // Easy way to have a hand-mouse when hovering over the goal. It hints clickability
                        	clickableGoal.innerHTML = cellData;
                        	$(td).append(clickableGoal);
                        	$(td).off().on('click',function(e){
                                e.preventDefault();
                                // If a click inside a text-input occurs, dont create another text input. if it occurs
                                // while cell has an 'a' element, then transform it to a text-input element
                                if (!($(td).children().is('form'))) {
                                    // A simple form with a default value equal to the current goal
                                    updateGoal = 'updateGoal';
									$(td).children().replaceWith("<form style='margin:0;min-width:255px;' name='updateGoalForm' id='updateGoalForm' >" +
                                    "<input id='updateGoal' class = 'editGoal' type='text' value='" + cellData + "'  style='margin:0'; /> " +
                                    "<a class='btn blueNavy' value='Ok' id='updateGoalFormSubmit' style='height:14px;width:5px;position:relative;left:-4px;'>"+
                                    "<i class='white halflings-icon ok-sign' style='position:relative;left:-3px;top:-3px;'></i></a></form>");

                                    // On 'Enter' update the goal tied to the activity
									$('#updateGoalForm').on('submit', function (event) {
										event.preventDefault();
										handleGoalAction(rowData.id, "updateGoal")

                                    });

                                    $('#updateGoalFormSubmit').click(function () {
										handleGoalAction(rowData.id, "updateGoal")
									});
                                }
                            });



                        	// If any click outside the currently edited goal occurs, then replace the text-input form
                        	// with just the name of the goal. The name is of course the cellData, which hasn't been updated
                        	// since the 'a' element became a 'form -> input ' element. So it has the old valu
                             $(document).on('mouseup',function(e) {
								 var container = $(td);
								 // if the target of the click isn't the container nor a descendant of the container
								 if (!container.is(e.target) && container.has(e.target).length === 0) {
                                    // update the goal if there was a search field present (for Mobile users who cant click 'Enter')
                                   /* if ($('#updateGoal').val() != null) {
                                         handleGoalAction(rowData.id, "updateGoal")

                                    }*/
								 $(td).children().replaceWith("<a href=''>" + cellData + "</a>");
								 }

                             });



						}
    				},
                   {
                    "targets": 2,
                    "createdCell": function(td, cellData, rowData, row, col) {
                        $(td).empty();
                        // We make activity clickable and tied with a showActivityModal Modal
							var ActivityLink = document.createElement('a');
							ActivityLink.href = BASE_URL + "activity/display-activity/" + (rowData.id).toString();
							$(ActivityLink).attr("data-target", "#showActivityGoalModal");
							$(ActivityLink).attr("data-toggle", "modal");
							ActivityLink.innerHTML = cellData;
							$(td).append(ActivityLink);

                    	}
                    },
                    {
					"targets": 3,
					"createdCell": function (td, cellData, rowData, row, col) {
						// Add colours for status
						var text = $(td).text();
						if (text == "InProgress"){
							text = "In Progress"
						}
						$(td).empty();
						$(td).className = "center";
                        // Colour status accordingly
						var StatusSpan = document.createElement('span');
						if (text == "Reached") {
							StatusSpan.className = 'label label-success';
						}
						else if (text == "Failed") {
							StatusSpan.className = 'label label-important';
						}
						else {
							StatusSpan.className = 'label label-warning';
						}
						StatusSpan.innerHTML = text; // Text and Colour of the goal Status  is contained in StatusSpan
                        // This associative array will help initialize the checked option correctly, since it is create through HTML-string
                        var DefaultCheck = {'Reached':"", 'InProgress':"", 'Failed':""};
						DefaultCheck[rowData.goal_status] = "Checked";
                        // Creating 'a' element to serve as parent of the popover
                        var goalStatusPopover = document.createElement('a');
                        goalStatusPopover.className = "popover-button";
                        $(goalStatusPopover).css( 'cursor', 'pointer' );
                        // creating the popover options
                        $(goalStatusPopover).css('outline','none');
                        $(goalStatusPopover).attr('tabindex','0');
						$(goalStatusPopover).attr('title','Change Status');
						$(goalStatusPopover).attr('data-toggle', 'popover');
						$(goalStatusPopover).attr('data-html', 'true');
						$(goalStatusPopover).attr('data-placement','top');
                        // Content of popover cant only be a text, so we added elements via Html-text as string
                        updateStatus = 'updateStatus'; // cant enter string inside a string inside another string any other way
                        var data_content = "" +
							"<form id='goalstatusTableEditForm' onchange=handleGoalAction("+ rowData.id +","+updateStatus+") >" +
							"<input type='radio' class='' name='goalstatus' " + DefaultCheck['Reached'] + " value='Reached' /><p style='color:green'>&nbsp;Reached</p>" +
							"<input type='radio' class='' name='goalstatus' " + DefaultCheck['InProgress'] + " value='InProgress' /><p style='color:orange'>&nbsp;In Progress</p>" +
							"<input type='radio' class='' name='goalstatus' " + DefaultCheck['Failed'] + " value='Failed'/><p style='color:red'>&nbsp;Failed</p>" +
							"</form>";
						$(goalStatusPopover).attr('data-content',data_content);
                        $(goalStatusPopover).popover();
                        goalStatusPopover.appendChild(StatusSpan);
						$(td).append(goalStatusPopover);
                        // In order to have only 1 popover active at a time, we close any other opened ones
						$(goalStatusPopover).on('click', function (e) {
							$('.popover-button').not(this).popover('hide');
						 });

						// To dismiss popover when a click outside the popover occurs
						$('body').on('click', function (e) {
							$('[data-toggle=popover]').each(function () {
								// hide any open popovers when the anywhere else in the body is clicked
								if (!$(this).is(e.target) && $(this).has(e.target).length === 0 && $('.popover').has(e.target).length === 0) {
									$(this).popover('hide');
								}
							});

						});
						}
					},
					{
					"targets": 4,
					"createdCell": function (td, cellData, rowData, row, col) {
						$(td).empty();
						$(td).className = "center";

						//Add Delete Button with modal trigger
						var buttonDelete = document.createElement('a');
						buttonDelete.className = "btn btn-danger btn-setting";
						buttonDelete.href = "#";
						buttonDelete.id = "DeleteId:"+ cellData.toString();
						$(buttonDelete).attr("data-target", "#deleteGoalModal");
						$(buttonDelete).attr("data-toggle", "modal");
						var iconTrash = document.createElement('i');
						iconTrash.className = "halflings-icon trash white";
						buttonDelete.appendChild(iconTrash);
						$(td).append(buttonDelete);
						$(buttonDelete).on('click', function(){
							// Dynamically change the 'deleteModal Content'
							$('#deleteGoalModal .modal-body p').text('Are you sure you want to delete goal: ' +
								'"' + rowData.goal + '". The Activity Linked will not be deleted');
							//So that only the LAST goal clicked will be deleted
                            var Id = $(buttonDelete).attr('id').split(":")[1];
                            // Disable all other instances, and apply function only for the currently shown modal
							$('#deleteGoalModalConfirm').off().on('click', function() {
								handleGoalAction(Id, "deleteGoal");
							})
						})
					}
				}]
			});

    function handleGoalAction(performs_id, setting) {
        Loading();
        var data="";
        if (setting == "updateGoal"){
            data = $('#updateGoal').val()
        }
        else if (setting == "updateStatus") {
            data = $('input:radio[name=goalstatus]:checked').val();
            $('.popover').popover('hide');
        }
		$.ajax({
				type: "post",
				data: {performs_id:performs_id, data:data, setting:setting, 'csrfmiddlewaretoken': getCookie('csrftoken')},
				cache: false,
				url: BASE_URL + 'goals/goalhandler/',
				dataType: "text",
				error: function (xhr, status, error) {
                    Done();
                    alert(xhr.responseText);
                    return

				},
				success: function (responseData) {
                    table.ajax.reload();
                    if (setting == "deleteGoal"){
                        $('#GoalsTitle').get(0).childNodes[2].nodeValue = "Goals ("+ responseData + ")" ;
						$('#deleteGoalModal').modal('hide');
                    }
					Done();
				}
			});

    }

	$('#showActivityGoalModal').on("hidden", function (e) {
        $(e.target).removeData("modal").find(".modal-body").empty();
	});


    $('#showActivityGoalModal').on("shown", function (e){
		try {
			initializeShowMap();
		}
		catch(err) {}
		$('#showActivityGoalModal h2 a')
		.attr('href',BASE_URL + "activity/" + $('.modal-body-replacement').attr('id'))
	});
