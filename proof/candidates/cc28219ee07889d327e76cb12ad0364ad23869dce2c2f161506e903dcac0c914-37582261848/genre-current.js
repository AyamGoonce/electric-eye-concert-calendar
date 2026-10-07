(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.74a4fac2953320c7.js","sha256":"74a4fac2953320c72a9f7f95b92395ad13924d7d866d8cbfb99ad2adc9f5b72b","count":244});
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
