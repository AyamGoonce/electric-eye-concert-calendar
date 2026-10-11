(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.ed279b771366bf2d.js","sha256":"ed279b771366bf2dc7ba49466fffb0ffff02e0065ed9d764717d9a14464898d6","count":2169,"publishedAt":"2026-10-11T13:01:56Z","state":"calendar-state.json","stateSha256":"c4ecec255d70e6b6c9c01d3587bebd3fd516f5fee2a795e7cf953b90eca89a54","sourceState":"calendar-source-state.json","sourceStateSha256":"172c67854a95f8087fe91f4b99ab2d6b87258cac6031f3c3ef9fd7b60922bbec"});
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
