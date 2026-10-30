(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.72eb8451fe236e87.js","sha256":"72eb8451fe236e87ea54ceeec16e6864e8736023cbeb5a42d346fe4f113f6d26","count":244});
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
