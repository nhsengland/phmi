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

/**
 * Update the "added" counter based on the number of <tr>s currently in the
 * table body.
 */
function updateCounter() {
  var count = $("#selected_orgs tr").length;
  var suffix = "";
  if (count === 0 || count >=2) {
    suffix = "s";
  };
  $("#num_added").text(count.toString() + " Organisation" + suffix);
}

$(document).ready(function () {
  $.getJSON("/organisations", function (data) {
    var control = $("#organisations");

    // configure with data from Django
    control.select2({
      data: data.results,
    });

    /**
     * Bind an event handler select2's select event
     */
    control.on("select2:select", function (event) {
      event.stopPropagation();
      selectOrganisation(event.params.data.id, event.params.data.text);
    });
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
