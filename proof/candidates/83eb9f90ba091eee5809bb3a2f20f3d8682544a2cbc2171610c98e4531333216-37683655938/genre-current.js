(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.dd3cdf79ac7159fd.js","sha256":"dd3cdf79ac7159fd95e61f95f3913c4235097ae731c3d1aa691b0709a9f6b9c1","count":244});
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
