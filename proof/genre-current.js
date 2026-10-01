(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.8572a019d11b5f34.js","sha256":"8572a019d11b5f3490a3571e1cf0a262b303c6f861bc23ebeaf4231519f91fad","count":208});
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
