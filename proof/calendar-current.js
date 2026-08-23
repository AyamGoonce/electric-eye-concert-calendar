(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.bfefc9f6d928e54b.js","sha256":"bfefc9f6d928e54b3a5abf808af1fae23e4f89a82b4b77c469d6ab4fc4a13e22","count":1708,"publishedAt":"2026-08-23T11:07:22Z","state":"calendar-state.json","stateSha256":"0910e8033e4133d224465070232a4b95d127f98c83561fa956d4b68ae2c01451"});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeConcertManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:concert-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:concert-data-error", {detail:{reason:"data asset unavailable"}}));
  };
  document.head.appendChild(script);
}());
