(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.e623c5821c7d0e80.js","sha256":"e623c5821c7d0e809a1becd1096c85fbad4fb7170df557771e773314e98f08e9","count":244});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeGenreManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:genre-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:genre-data-error", {detail:{reason:"genre data unavailable"}}));
  };
  document.head.appendChild(script);
}());
