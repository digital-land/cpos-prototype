
// Needs to come after GOV.UK js because makes use of:
// 	* 'govuk-frontend/govuk/vendor/polyfills/Function/prototype/bind'
// 	* 'govuk-frontend/govuk/common' {nodeListForEach}

function nodeListForEach (nodes, callback) {
  if (window.NodeList.prototype.forEach) {
    return nodes.forEach(callback)
  }
  for (var i = 0; i < nodes.length; i++) {
    callback.call(window, nodes[i], i, nodes)
  }
}

// Back to top module as seen in govuk-design-system
// https://github.com/alphagov/govuk-design-system/blob/master/src/javascripts/components/back-to-top.js
function BackToTop ($module, options) {
  this.$module = $module
  this.$observedElement = options.$observedElement
  this.intersectionRatio = 0
}

BackToTop.prototype.init = function () {
  var $observedElement = this.$observedElement

  // If there's no element for the back to top to follow, exit early.
  if (!$observedElement) {
    return
  }

  if (!('IntersectionObserver' in window)) {
    // If there's no support fallback to regular sticky behaviour
    return this.update()
  }

  // Create new IntersectionObserver
  var observer = new window.IntersectionObserver(function (entries) {
    // Available data when an intersection happens
    // Back to top visibility
    // Element enters the viewport
    if (entries[0].intersectionRatio !== 0) {
      // How much of the element is visible
      this.intersectionRatio = entries[0].intersectionRatio
    // Element leaves the viewport
    } else {
      this.intersectionRatio = 0
    }
    this.update()
  }.bind(this), {
    // Call the observer, when the element enters the viewport,
    // when 25%, 50%, 75% and the whole element are visible
    threshold: [0, 0.25, 0.5, 0.75, 1]
  })

  observer.observe($observedElement)
}

BackToTop.prototype.update = function () {
  var thresholdPercent = (this.intersectionRatio * 100)

  if (thresholdPercent === 100) {
    this.hide()
  } else if (thresholdPercent < 90) {
    this.show()
  }
}

BackToTop.prototype.hide = function () {
  this.$module.classList.add('app-back-to-top--hidden')
}

BackToTop.prototype.show = function () {
  this.$module.classList.remove('app-back-to-top--hidden')
}


// ================================
// Selected counts for filters
// ================================

function SelectedCounter($module) {
  this.$module = $module
  this.$fieldset = $module.querySelector("fieldset")
  this.$inputs = this.$fieldset.querySelectorAll("input")
}

SelectedCounter.prototype.init = function() {
  var $module = this.$module
  var $inputs = this.$inputs

  // if no inputs then return
  if (!$inputs) {
    return
  }

  //
  var boundFetchCountElement = this.fetchCountElement.bind(this)
  this.countMessage = boundFetchCountElement()

  // if current count is 0 hide the message
  this.message_is_hidden = false
  if(this.currentCount == 0) {
    this.hideCountMessage()
  }

  // Bind event changes to the textarea
  var boundChangeEvents = this.bindChangeEvents.bind(this)
  boundChangeEvents()
}

SelectedCounter.prototype.fetchCountElement = function() {
  var $module = this.$module
  var countMessage = $module.querySelector(".filter-group__selected-text")

  // if the count message doesn;t exist, create one
  if(!countMessage) {
    countMessage = this.createCountElement()
  }

  this.countElement = countMessage.querySelector(".filter-group__selected-text__count")
  this.currentCount = parseInt(this.countElement.textContent)

  return countMessage
}

SelectedCounter.prototype.createCountElement = function() {
  var $module = this.$module
  var $summary = $module.querySelector(".filter-group__summary");
  var firstIcon = $summary.querySelector("svg")

  var countMessage = document.createElement("span")
  countMessage.classList.add("filter-group__selected-text")
  countMessage.textContent = " selected"
  firstIcon.insertAdjacentElement('beforebegin', countMessage)

  countMessage.insertAdjacentHTML('afterbegin', '<span class="filter-group__selected-text__count">0</span>' )
  
  return countMessage
}

SelectedCounter.prototype.bindChangeEvents = function() {
  var $inputs = this.$inputs
  //console.log(this)
  $inputs.forEach(input => {
    input.addEventListener('change', this.updateCount.bind(this))
  })
}

SelectedCounter.prototype.updateCount = function() {
  var $fieldset = this.$fieldset
  var count = $fieldset.querySelectorAll("input:checked").length

  // if 0 hide
  if(count == 0) {
    this.countElement.textContent = 0
    this.hideCountMessage()
  } else if (count != this.currentCount) {
    // if changed update
    this.countElement.textContent = count
    this.showCountMessage()
  }
  // if same, do nothing ----
  
  this.currentCount = count
}

SelectedCounter.prototype.hideCountMessage = function() {
  this.countMessage.classList.add("govuk-visually-hidden")
  this.message_is_hidden = true
}

SelectedCounter.prototype.showCountMessage = function() {
  this.countMessage.classList.remove("govuk-visually-hidden")
  this.message_is_hidden = false
}
