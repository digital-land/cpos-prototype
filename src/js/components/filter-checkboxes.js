import '../../govuk/vendor/polyfills/Function/prototype/bind';


// ====================================
// Filter checkboxes module
// ====================================

// to do (see https://www.gov.uk/search/all?keywords=publications&content_purpose_supergroup%5B%5D=services&organisations%5B%5D=academy-for-social-justice&order=relevance)
// - aria-describedby, hidden span that counts how many options are showing and how many of them are selected
// - aria-controls, indicate that it controls the list of checkboxes
// - hide textbox when no js

function FilterCheckboxes($module) {
  this.$module = $module
  this.$textbox = $module.querySelector('.filter-group__auto-filter__input')
  this.checkboxArr = [...$module.querySelectorAll(".govuk-checkboxes__item")]
}

FilterCheckboxes.prototype.init = function() {
  var $module = this.$module
  var $checkboxes = this.checkboxArr

  // if no checkboxes then return
  if (!$checkboxes) {
    return
  }

  // Bind event changes to the textarea
  var boundInputEvents = this.bindInputEvents.bind(this)
  boundInputEvents()
}

FilterCheckboxes.prototype.bindInputEvents = function() {
  var $textbox = this.$textbox;

  $textbox.addEventListener('input', this.filterCheckboxes.bind(this))
}

FilterCheckboxes.prototype.filterCheckboxes = function() {
  var $textbox = this.$textbox
  var boundFilterCheckboxesArr = this.filterCheckboxesArr.bind(this)
  // filter the array of checkboxes
  var reducedArr = boundFilterCheckboxesArr($textbox.value)

  // show only those checkboxes remaining
  var boundDisplayMatchingCheckboxes = this.displayMatchingCheckboxes.bind(this)
  boundDisplayMatchingCheckboxes(reducedArr)
}

FilterCheckboxes.prototype.filterCheckboxesArr = function(query) {
  var checkboxArr = this.checkboxArr
  return checkboxArr.filter(function(el) {
    const checkbox = el.querySelector('label');
    return checkbox.textContent.toLowerCase().indexOf(query.toLowerCase()) !== -1;
  })
}

FilterCheckboxes.prototype.displayMatchingCheckboxes = function(ckbxArr) {
  // hide all
  this.checkboxArr.forEach((ckbx) => ckbx.style.display = 'none');
  // re show those in filtered array
  ckbxArr.forEach((ckbx) => ckbx.style.display = 'block');
}


export default FilterCheckboxes