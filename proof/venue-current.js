(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.8d0bd2442d245695.js","sha256":"8d0bd2442d245695c41b69dff8792dc134810aa18f1aaa72d1934eabc9772c85","count":109});
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
