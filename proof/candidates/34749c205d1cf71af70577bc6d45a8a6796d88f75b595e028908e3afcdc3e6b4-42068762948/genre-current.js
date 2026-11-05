(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.375db20b6b9dd315.js","sha256":"375db20b6b9dd3154d2276fb1827c0b1380b75def5fae707a2dff04d35c2fda8","count":244});
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
