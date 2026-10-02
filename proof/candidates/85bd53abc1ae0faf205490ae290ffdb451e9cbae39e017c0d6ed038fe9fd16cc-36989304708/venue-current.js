(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.5b5df1004a08e49c.js","sha256":"5b5df1004a08e49cbfb29c20264edbcb24cae2399ea74b3c58dab5a24539b7ce","count":109});
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
