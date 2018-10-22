ROW_TEMPLATE = `
<tr>
  <td>
    <input type="hidden" name="organisations" value="ID" />
    TEXT
  </td>
  <td class="text-right"><a href="#">Remove</a></td>
</tr>
`;

/**
 * Add the selected Organisation to the selected Orgs table
 */
function selectOrganisation(id, text) {

  if (id === "empty") {
    return;
  }

  // check the given id doesn't alredy exist
  var existing_ids = $("#selected_orgs input").map(function (index, element) {
    return $(element).val();
  }).get();
  if (existing_ids.indexOf(id.toString()) > -1) {
    return;
  }

  // Replace the ID and TEXT placeholders in the template with our real values
  var new_row = ROW_TEMPLATE.replace("ID", id).replace("TEXT", text);

  // Parse the template string into HTML and append it to the table body as a
  // new row.
  $("#selected_orgs").append($.parseHTML(new_row));

  updateCounter();
}


/*
* Returns the number of of <tr>s currently in the
* table body.
*/
function getOrgCount(){
  return $("#selected_orgs tr").length;
}

/**
 * Update the "added" counter based on the number orgs
 */
function updateCounter() {
  var count = getOrgCount();
  var suffix = "";
  if (count === 0 || count >=2) {
    suffix = "s";
  };
  $("#num_added").text(count.toString() + " Organisation" + suffix);
  showRemoveAll();
}


/*
* Only show the remove all button if we have orgs
*/
function showRemoveAll(){
  var count = getOrgCount();

  if(count){
    $("#remove_all").show();
  }
  else{
    $("#remove_all").hide();
  }
}

$(document).ready(function () {
  // ADD OR EDIT VIEW
  var options = {
    valueNames: ['name']
  };
  var orgList = new List('org_list', options);
  showRemoveAll();

  /**
   * Bind the click handler to each <li> in the orgs list
   */
  $(".org").click(function (event) {
    selectOrganisation(
      event.currentTarget.id,
      event.currentTarget.firstElementChild.textContent
    );
  });

  /**
   * Bind a click handler to the remove links so we can remove its parent <tr>
   * element on click.
   *
   * Using the .on() method here because rows are dynamically added.
   */
  $("#selected_orgs").on("click", "tr td a", function (event) {
    event.stopPropagation();
    event.target.parentElement.parentElement.remove();
    updateCounter();
  })

  /**
   * Bind a click handler to the remove all link so we can remove all <tr>s in
   * the table body on click.
   */
  $("#remove_all").click(function (event) {
    event.stopPropagation();
    $("#selected_orgs tr").remove();
    updateCounter();
  })
});


