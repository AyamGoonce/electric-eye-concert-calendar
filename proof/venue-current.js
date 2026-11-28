(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.ef42ac089ae38aca.js","sha256":"ef42ac089ae38aca60750de5a5ee7566e5047a03b8d94df71d71872465eb65ac","count":181});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeVenueManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:venue-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:venue-data-error", {detail:{reason:"venue data unavailable"}}));
  };
  document.head.appendChild(script);
}());
